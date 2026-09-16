# CLI reference

Installing eKoNLPy provides the `ekonlpy` command:

```bash
ekonlpy --help
ekonlpy --version
```

The command accepts these options:

| Option | Default | Meaning |
| --- | --- | --- |
| `--tagger`, `-t` | `ekonlpy` | Select `ekonlpy` for the extended tagger or `mecab` for the original path. |
| `--input`, `-i` | none | Text to tag. |
| `--help`, `-h` | | Show help. |
| `--version` | | Show the installed version. |

Examples:

```bash
ekonlpy --input "금통위는 금리정책을 결정했다."
ekonlpy --tagger mecab --input "금통위는 금리정책을 결정했다."
```

With no `--input`, the command prints its help text. The CLI prints Python list
syntax containing `(surface, tag)` pairs; it does not read files or emit JSON.
