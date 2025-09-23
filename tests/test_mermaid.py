from prop.generator_diagrams import render_mermaid_to_png

def test_mermaid_renderer_basic():
    sample = """graph TD\nA[Start] --> B{Choice}\nB -->|One| C[Path 1]\nB -->|Two| D[Path 2]\n"""
    png = render_mermaid_to_png(sample)
    assert isinstance(png, (bytes, bytearray))
    # Should produce some bytes (> 100 with mmdc, fallback may be small but > 0)
    assert len(png) > 0
