import os

def build_standalone():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(base_dir, "frontend", "static")
    
    index_file = os.path.join(static_dir, "index.html")
    css_file = os.path.join(static_dir, "css", "stitch.css")
    js_file = os.path.join(static_dir, "js", "app.js")
    output_file = os.path.join(static_dir, "standalone_app.html")

    with open(index_file, "r", encoding="utf-8") as f:
        html = f.read()

    with open(css_file, "r", encoding="utf-8") as f:
        css = f.read()

    with open(js_file, "r", encoding="utf-8") as f:
        js = f.read()

    html = html.replace('<link rel="stylesheet" href="/static/css/stitch.css"/>', f'<style>\n{css}\n</style>')
    html = html.replace('<script src="/static/js/app.js"></script>', f'<script>\n{js}\n</script>')

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated standalone_app.html successfully ({os.path.getsize(output_file)} bytes).")

if __name__ == "__main__":
    build_standalone()
