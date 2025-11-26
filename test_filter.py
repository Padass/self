import re

def clean_message_content(content):
    # Pattern to match leading mentions, emojis, and whitespace
    # We will use a loop to repeatedly strip these patterns from the start of the string
    
    while True:
        original = content
        # Remove Discord mentions <@123>, <@!123>, <@&123>
        content = re.sub(r'^\s*<@&?!?[0-9]+>\s*', '', content)
        # Remove Discord custom emojis <a:name:123>
        content = re.sub(r'^\s*<a?:\w+:[0-9]+>\s*', '', content)
        # Remove text mentions @name (non-whitespace characters after @)
        content = re.sub(r'^\s*@\S+\s*', '', content)
        # Remove text emojis :name: or :name~1:
        content = re.sub(r'^\s*:[^:\s]+:\s*', '', content)
        # Remove unicode emojis and other symbols. 
        # Using a broad range for symbols/emojis at the start.
        # This regex matches non-word characters that are not standard punctuation for sentence starts.
        # We want to keep normal text.
        # Let's try matching specific emoji ranges or just non-alphanumeric/non-punctuation.
        # A simple heuristic: if it's not a letter, number, or common punctuation, strip it.
        # But we need to be careful not to strip "Hello" or "(Important)".
        
        # For the specific user examples: 🤠, 🧑‍🌾, 🌦️, 🌿
        # These are all unicode characters.
        # Let's use the 'emoji' library if available? No, standard lib only.
        
        # Regex for unicode emojis is complex. 
        # Let's try a simpler approach for the specific examples given:
        # Match non-ascii characters at the start?
        # But Vietnamese characters are non-ascii.
        
        # Let's look at the examples again.
        # ":cucquang: Cực Quang đang xuất hiện!!" -> "Cực Quang..." (Starts with alphanumeric)
        # "@cucquang ... Hạt Giống..." -> "Hạt Giống..." (Starts with alphanumeric)
        
        # Maybe we just strip everything until we hit a "word" character that is likely part of the message?
        # But "Cực" starts with 'C'.
        
        # Let's try to strip specific "symbol-like" things.
        # [^\w\s] matches symbols.
        # But we want to keep Vietnamese characters.
        # \w in Python 3 matches Unicode word characters (including Vietnamese).
        # So [^\w\s] should match emojis but NOT Vietnamese letters.
        
        # However, we also want to keep punctuation like "Hello!" or "(Info)".
        # So we shouldn't strip `(` or `[`.
        
        # Let's try to strip:
        # - Mentions/Tags (handled above)
        # - Emojis (which are usually non-word, non-punctuation)
        
        # Let's refine the "symbol" regex.
        # We want to remove things that are NOT:
        # - Word characters (letters, numbers, underscores)
        # - Common punctuation (.,!?;:'"()[]{})
        # - Whitespace
        
        # So we remove: [^\w\s.,!?;:'"()\[\]{}]
        
        content = re.sub(r'^\s*[^\w\s.,!?;:\'"()\[\]{}-]+\s*', '', content)
        
        if content == original:
            break
            
    return content.strip()

examples = [
    (":cucquang: Cực Quang đang xuất hiện!!", "Cực Quang đang xuất hiện!!"),
    ("@cucquang @🤠 @🧑‍🌾 @🌦️ Hạt Giống Bí Ngô đang bán trong Shop!!", "Hạt Giống Bí Ngô đang bán trong Shop!!"),
    ("@bingo @🤠 @🧑‍🌾 @🌿 nó như hế này tôi muốn lọc lấy nội ung chính thôi", "nó như hế này tôi muốn lọc lấy nội ung chính thôi"),
    (":voixanh: Vòi Xanh đang bán trong Shop!!", "Vòi Xanh đang bán trong Shop!!"),
    ("@voixanh @🤠 @🧑‍🌾 @🚿 Vòi Xanh đang bán trong Shop!!", "Vòi Xanh đang bán trong Shop!!"),
    (":watermelon~1: Hạt Giống Dưa Hấu đang bán trong Shop!!", "Hạt Giống Dưa Hấu đang bán trong Shop!!"),
    ("@duahau @🤠 @🧑‍🌾 @🌿 Hạt Giống Dưa Hấu đang bán trong Shop!!", "Hạt Giống Dưa Hấu đang bán trong Shop!!")
]

import sys
sys.stdout.reconfigure(encoding='utf-8')

for inp, expected in examples:
    result = clean_message_content(inp)
    match = result == expected
    print(f"Input:    {inp}")
    print(f"Expected: {expected}")
    print(f"Got:      {result}")
    print(f"Match:    {match}")
    print("-" * 20)
