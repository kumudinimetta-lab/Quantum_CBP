import os
import urllib.request

pdfs = [
    ("Draper_2000_Addition.pdf", "http://arxiv.org/pdf/quant-ph/0008033v1.pdf"),
    ("Vedral_1996_Arithmetic.pdf", "http://arxiv.org/pdf/quant-ph/9511018v1.pdf"),
    ("Thapliyal_2016_Division.pdf", "http://arxiv.org/pdf/1609.01241v1.pdf")
]

target_dir = r"c:\CBP\HybridQuantumKnapsack\references\papers\pdfs"
os.makedirs(target_dir, exist_ok=True)

for filename, url in pdfs:
    filepath = os.path.join(target_dir, filename)
    print(f"Downloading {filename} from {url} to {filepath}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"Success: {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")
