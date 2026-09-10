# ☽ 𝗆𝐨𝐨𝗇 𝗍𝐞𝐚𝗋𝗌 ☾

rain gathers below the letters; the number of drops remembers a digit.

Recovered Moon Tears: three base-six digits per ASCII character, or four per UTF-8 byte. Each digit is a stack of two through seven reserved combining marks. One mark is decorative. This is distinct from Zalgo's digit-by-mark identities and Diacritic Bloom's selector channel.

Open `index.html` for the offline browser demo / Pages entry point. Run `python -m unittest -v` or `python moon_tears.py --help` for the CLI. No dependencies, uploads or keys.

The two modes and mark order are historical. `historical/` preserves the original Python, HTML, carrier and honeysuckle specimen from `moon_tears_cipher_bundle.zip` byte for byte. The loose `raindrop_honeysuckle_ciphertext.txt` is instead a Vigenère/LSB experiment and is kept with background context, not claimed as this codec's vector. Hardened adapters now reject out-of-domain decoded values, overgrown stacks, invalid UTF-8 and reserved marks already in a carrier; the browser preserves a leading BOM and clears stale output on failure. These are new validation decisions, not a new wire format.

There is no length field or checksum in this format. Some damaged strings can still decode to plausible but wrong text; a complete digit-group truncation is undetectable. Do not normalize the encoded Unicode. It is a puzzle encoding, not encryption or a reliable storage protocol. Keep originals and the selected mode.

Private review source recovered September 10 2026 from `cipher_documents/documents` in Ashleigh's project archive. Exact original publication date and license were not established; no new license is imposed. Public Pages deployment awaits owner review.
