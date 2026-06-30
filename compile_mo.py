import struct


def unescape(s):
    """Handle .po escape sequences without corrupting non-ASCII chars."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            c = s[i + 1]
            if c == 'n':
                result.append('\n')
            elif c == 't':
                result.append('\t')
            elif c == 'r':
                result.append('\r')
            elif c == '\\':
                result.append('\\')
            elif c == '"':
                result.append('"')
            else:
                result.append('\\')
                result.append(c)
            i += 2
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


def compile_po(po_path, mo_path):
    entries = {}
    msgid = msgstr = None
    in_msgid = in_msgstr = False

    with open(po_path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('msgid '):
                if msgid is not None and msgstr is not None:
                    entries[msgid] = msgstr
                raw = line[6:].strip().strip('"')
                msgid = unescape(raw)
                msgstr = None
                in_msgid = True
                in_msgstr = False
            elif line.startswith('msgstr '):
                raw = line[7:].strip().strip('"')
                msgstr = unescape(raw)
                in_msgid = False
                in_msgstr = True
            elif line.startswith('"'):
                raw = line.strip().strip('"')
                chunk = unescape(raw)
                if in_msgid and msgid is not None:
                    msgid += chunk
                elif in_msgstr and msgstr is not None:
                    msgstr += chunk
            else:
                in_msgid = in_msgstr = False

    if msgid is not None and msgstr is not None:
        entries[msgid] = msgstr

    # Keep header entry (empty msgid="" → metadata with charset=UTF-8)
    # Only skip entries where msgstr is empty AND it's not the header
    entries = {k: v for k, v in entries.items() if v or k == ''}

    keys = sorted(entries.keys())
    ids_blob = b''
    strs_blob = b''
    k_offsets = []
    v_offsets = []

    for k in keys:
        kb = k.encode('utf-8')
        k_offsets.append((len(kb), len(ids_blob)))
        ids_blob += kb + b'\x00'

    for k in keys:
        vb = entries[k].encode('utf-8')
        v_offsets.append((len(vb), len(strs_blob)))
        strs_blob += vb + b'\x00'

    n = len(keys)
    # .mo header: magic, revision, N, orig_offset, trans_offset, hash_size, hash_offset
    header_size = 28
    orig_table_offset = header_size
    trans_table_offset = header_size + n * 8
    ids_start = trans_table_offset + n * 8
    strs_start = ids_start + len(ids_blob)

    output = struct.pack('<IIIIIII',
        0x950412de, 0, n,
        orig_table_offset, trans_table_offset,
        0, 0)

    for length, offset in k_offsets:
        output += struct.pack('<II', length, ids_start + offset)
    for length, offset in v_offsets:
        output += struct.pack('<II', length, strs_start + offset)

    output += ids_blob + strs_blob

    with open(mo_path, 'wb') as f:
        f.write(output)

    print(f'OK: compiled {n} strings to {mo_path}')


if __name__ == '__main__':
    compile_po(
        'locale/uk/LC_MESSAGES/django.po',
        'locale/uk/LC_MESSAGES/django.mo',
    )
