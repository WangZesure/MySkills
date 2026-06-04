# ICS Debug Reference — NEMU/Emulator-Specific Details

> ⚠️ 本文件是通用方法论（SKILL.md）的栈特定附录。请先阅读 **SKILL.md** 中的核心模式，再回来查具体的 NEMU 数据流图和陷阱清单。

## Subsystem Data Flow Maps

### 1. VGA Framebuffer Write Path

```
PAL: NDL_Render(canvas)
  │
  ▼
libndl: memcpy(fb, canvas, W*H*4)    // fb = (uint32_t*)0xbf000000
  │
  ▼
CPU: vaddr_write(0xbf000000+off, data)
  │
  ▼
MMU: page_translate(0xbf000000, WRITE)
  │  ├─ CR0.PG==0? → PA=vaddr (identity, no paging)
  │  ├─ vaddr < 128MB? → PA=vaddr (fast path, identity mapping)
  │  └─ else: walk PDE→PTE, PA=pte.frame<<12|offset
  │
  ▼
memory: paddr_write(phys_addr, data)
  │  ├─ is_mmio(addr)!=-1? → mmio_write → mmio_space_pool[addr-0x40000]
  │  └─ else:               → memcpy(pmem+addr, data)
  │
  ▼
device: vga_update_screen()  [called by device_update at 50Hz]
  │  SDL_UpdateTexture from mmio_space_pool
  │
  ▼
SDL window
```

**Key routing points where bugs hide:**
- `page_translate`: fast path must cover 0xbf000000 (user fb mapping)
- `paddr_write`: must call `is_mmio()` before `memcpy(pmem)`
- PDE/PTE setup in `load_prog`: 0xbf000000→0x40000 mapping

### 2. Keyboard Event Path

```
Physical: SDL_KEYDOWN/KEYUP
  │
  ▼
device/keyboard.c: send_key(scancode, is_keydown)
  │  maps SDL scancode → AM keycode (e.g. _KEY_SPACE)
  │  key | (is_keydown ? 0x8000 : 0) → key_queue
  │  status_reg |= 1
  │
  ▼
AM/ioe.c: _read_key()
  │  if (inb(0x64) & 1) return inl(0x60);
  │  return _KEY_NONE;
  │
  ▼
nanos-lite/device.c: events_read()
  │  snprintf(evt_buf, "kd %s\n", keyname[code]);
  │  evt_len = strlen(evt_buf);  // NOT snprintf return!
  │
  ▼
navy-apps: NDL_WaitEvent() reads from /dev/events
  │  parses "kd SPACE\n" → key event
  │
  ▼
PAL: input handler
```

**Key routing points where bugs hide:**
- `snprintf` return vs `strlen` for event length
- Single event per call (batching overflows NDL buffer)
- keycode bit 15 = keydown flag

### 3. File I/O Path

```
PAL: fopen("word.dat") → fread(buf, size)
  │
  ▼
libc: _read(fd, buf, size)
  │
  ▼
nanos-lite/fs.c: fs_read(fd, buf, size)
  │  offset = file_table[fd].offset
  │  ramdisk_read(buf, offset, size)
  │  file_table[fd].offset += size
  │
  ▼
ramdisk (embedded in kernel image)

fstat path:
  PAL: fstat(fd, &statbuf) → statbuf.st_size
    │
    ▼
  libos/nanos.c: _fstat(fd, buf)
    buf->st_size = _lseek(fd, 0, SEEK_END)  // must seek, not 0!
```

**Key routing points where bugs hide:**
- `_fstat`: `st_size` must use `_lseek(SEEK_END)`, not hardcoded 0
- `files.h` must match `ramdisk.img` (same find order during build)
- `file_table[fd].offset` must be per-fd, updated on read/write/lseek

### 4. CPU Instruction Execution Path

```
exec_wrapper:
  decoding.seq_eip = cpu.eip
  exec_real(&decoding.seq_eip):
    opcode = instr_fetch(eip, 1)
    if opcode == 0x0F: → 2byte_esc
    set_width(opcode_table[opcode].width)
    idex(eip, &opcode_table[opcode]):
      decode(eip)   → fills decoding.src/dest/src2
      execute(eip)  → RTL operations
  update_eip()
```

**Opcode table lookup:**
```
opcode_table[512]:
  [0..255]   one-byte opcodes
  [256..511] two-byte opcodes (0x0F xx)

Group instructions (gp1..gp7):
  opcode → group table[ext_opcode]
  ext_opcode = ModR_M.reg (bits [5:3] of ModR/M byte)
```

## Common Pitfalls Checklist

When debugging, eliminate these first:

| # | Pitfall | File | Symptom | Fix |
|---|---------|------|---------|-----|
| 1 | `#define DIFF_TEST` | `nemu/include/common.h` | 100x slowdown | comment out |
| 2 | `#define DEBUG` | `nemu/include/common.h` | moderate slowdown | comment out |
| 3 | `paddr_write` missing `is_mmio()` | `nemu/src/memory/memory.c` | VGA black screen | add mmio routing |
| 4 | `_fstat` hardcodes `st_size=0` | `navy-apps/libs/libos/src/nanos.c` | empty file reads | use `_lseek(SEEK_END)` |
| 5 | `snprintf` return for event len | `nanos-lite/src/device.c` | keyboard overflow | use `strlen(evt_buf)` |
| 6 | Missing decode declaration | `nemu/include/cpu/decode.h` | undeclared compile error | add `make_DHelper(name)` |
| 7 | `files.h` stale vs `ramdisk.img` | `nanos-lite/src/` | wrong file content | rebuild both together |
| 8 | page_translate missing fast path | `nemu/src/memory/memory.c` | performance drop | add `if (vaddr < PMEM_SIZE) return vaddr` |

## Opcode Analysis Cheat Sheet

### gp2 group (0xC0/0xC1/0xD0/0xD1/0xD2/0xD3): Rotate/Shift

```
ext_opcode → instruction
  0 → ROL    1 → ROR    2 → RCL    3 → RCR
  4 → SHL    5 → SHR    6 → —      7 → SAR
```

### Two-byte instructions that were missing (PA4→PA5)

```
0x0F 0xA4 → SHLD r/m, r, imm8   0x0F 0xA5 → SHLD r/m, r, CL
0x0F 0xAC → SHRD r/m, r, imm8   0x0F 0xAD → SHRD r/m, r, CL
```

### Decode function naming in opcode table

```
IDEX(decoder, executor)     → width=0 (follows operand_size: 16 or 32)
IDEXW(decoder, executor, w) → fixed width (1=byte, 2=word, 4=dword)
EMPTY                       → exec_inv (invalid opcode trap)
```

### Required for every new instruction

1. `all-instr.h`: `make_EHelper(name)`
2. `logic.c` (or appropriate file): `make_EHelper(name) { ... }`
3. `exec.c`: table entry in correct position
4. `decode.c` (if custom decode): `make_DHelper(name) { ... }`
5. `decode.h`: `make_DHelper(name);` declaration
