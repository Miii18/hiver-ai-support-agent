"""Generate Phase 9 architecture diagrams as SVG."""
from pathlib import Path


def generate_architecture_svg() -> str:
    """Generate architecture diagram showing component flow."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .box { fill: #121c2b; stroke: #ff9900; stroke-width: 2; }
      .text { fill: #eaf2ff; font-family: sans-serif; font-size: 14px; text-anchor: middle; }
      .label { fill: #ff9900; font-weight: bold; }
      .arrow { stroke: #ff9900; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="#ff9900" />
    </marker>
  </defs>

  <!-- Background -->
  <rect width="1000" height="600" fill="#0b1220"/>

  <!-- Title -->
  <text x="500" y="30" class="text" style="font-size: 20px; font-weight: bold;">Phase 9: Production Frontend Architecture</text>

  <!-- Streamlit UI -->
  <rect x="50" y="80" width="180" height="80" class="box"/>
  <text x="140" y="115" class="label">Streamlit UI</text>
  <text x="140" y="135" class="text" style="font-size: 12px;">Chat Interface</text>
  <text x="140" y="150" class="text" style="font-size: 12px;">Dark Theme</text>

  <!-- FastAPI Backend -->
  <rect x="310" y="80" width="180" height="80" class="box"/>
  <text x="400" y="115" class="label">FastAPI Backend</text>
  <text x="400" y="135" class="text" style="font-size: 12px;">/chat /health</text>
  <text x="400" y="150" class="text" style="font-size: 12px;">/intents /reset</text>

  <!-- FAISS Retriever -->
  <rect x="570" y="80" width="180" height="80" class="box"/>
  <text x="660" y="115" class="label">FAISS Retriever</text>
  <text x="660" y="135" class="text" style="font-size: 12px;">Vector Index</text>
  <text x="660" y="150" class="text" style="font-size: 12px;">Semantic Search</text>

  <!-- Knowledge Base -->
  <rect x="830" y="80" width="120" height="80" class="box"/>
  <text x="890" y="115" class="label">Knowledge</text>
  <text x="890" y="135" class="text" style="font-size: 12px;">Embeddings</text>

  <!-- Flow arrows -->
  <path d="M 230 120 L 310 120" class="arrow"/>
  <path d="M 490 120 L 570 120" class="arrow"/>
  <path d="M 750 120 L 830 120" class="arrow"/>

  <!-- Components -->
  <rect x="50" y="250" width="220" height="100" class="box"/>
  <text x="160" y="275" class="label">UI Components</text>
  <text x="160" y="295" class="text" style="font-size: 12px;">- Chat bubbles</text>
  <text x="160" y="315" class="text" style="font-size: 12px;">- Source cards</text>
  <text x="160" y="335" class="text" style="font-size: 12px;">- Intent badges</text>

  <!-- API Client -->
  <rect x="340" y="250" width="220" height="100" class="box"/>
  <text x="450" y="275" class="label">API Client</text>
  <text x="450" y="295" class="text" style="font-size: 12px;">- Retry logic</text>
  <text x="450" y="315" class="text" style="font-size: 12px;">- Timeout handling</text>
  <text x="450" y="335" class="text" style="font-size: 12px;">- Error handling</text>

  <!-- Theme -->
  <rect x="630" y="250" width="220" height="100" class="box"/>
  <text x="740" y="275" class="label">Dark Theme</text>
  <text x="740" y="295" class="text" style="font-size: 12px;">- Navy primary</text>
  <text x="740" y="315" class="text" style="font-size: 12px;">- Orange accent</text>
  <text x="740" y="335" class="text" style="font-size: 12px;">- Responsive</text>

  <!-- Features -->
  <rect x="50" y="420" width="800" height="130" class="box"/>
  <text x="450" y="445" class="label">Key Features</text>
  <text x="70" y="470" class="text" style="text-anchor: start; font-size: 12px;">• Multiple conversation turns with session persistence</text>
  <text x="70" y="490" class="text" style="text-anchor: start; font-size: 12px;">• Chat export (JSON/Markdown), confidence meter, intent detection</text>
  <text x="70" y="510" class="text" style="text-anchor: start; font-size: 12px;">• Retrieved source cards with similarity scores, typing animation</text>
  <text x="70" y="530" class="text" style="text-anchor: start; font-size: 12px;">• Dark/light mode toggle, mobile-responsive layout</text>
</svg>"""


def generate_deployment_svg() -> str:
    """Generate deployment architecture diagram."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .box { fill: #121c2b; stroke: #ff9900; stroke-width: 2; }
      .text { fill: #eaf2ff; font-family: sans-serif; font-size: 14px; text-anchor: middle; }
      .label { fill: #ff9900; font-weight: bold; }
      .arrow { stroke: #ff9900; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }
      .service { fill: #1a2634; stroke: #ff9900; stroke-width: 2; }
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="#ff9900" />
    </marker>
  </defs>

  <!-- Background -->
  <rect width="1000" height="600" fill="#0b1220"/>

  <!-- Title -->
  <text x="500" y="30" class="text" style="font-size: 20px; font-weight: bold;">Phase 9: Production Deployment Architecture</text>

  <!-- Docker Section -->
  <rect x="40" y="70" width="400" height="480" class="service" style="stroke-dasharray: 5,5;"/>
  <text x="240" y="100" class="label">Docker Compose (Local)</text>

  <rect x="60" y="130" width="160" height="80" class="box"/>
  <text x="140" y="160" class="label">Backend Container</text>
  <text x="140" y="180" class="text" style="font-size: 12px;">Port 8000</text>

  <rect x="260" y="130" width="160" height="80" class="box"/>
  <text x="340" y="160" class="label">Frontend Container</text>
  <text x="340" y="180" class="text" style="font-size: 12px;">Port 8501</text>

  <!-- Render Section -->
  <rect x="520" y="70" width="440" height="230" class="service" style="stroke-dasharray: 5,5;"/>
  <text x="740" y="100" class="label">Render Deployment</text>

  <rect x="540" y="130" width="190" height="80" class="box"/>
  <text x="635" y="160" class="label">Backend Service</text>
  <text x="635" y="180" class="text" style="font-size: 12px;">Free tier Oregon</text>

  <rect x="770" y="130" width="170" height="80" class="box"/>
  <text x="855" y="160" class="label">Frontend Service</text>
  <text x="855" y="180" class="text" style="font-size: 12px;">Free tier Oregon</text>

  <!-- Railway Section -->
  <rect x="520" y="330" width="440" height="220" class="service" style="stroke-dasharray: 5,5;"/>
  <text x="740" y="360" class="label">Railway Deployment</text>

  <rect x="540" y="390" width="400" height="60" class="box"/>
  <text x="740" y="415" class="label">Backend Service (Python 3.11)</text>

  <!-- Features -->
  <rect x="40" y="570" width="920" height="20" fill="none" stroke="#ff9900" stroke-width="1"/>
  <text x="50" y="584" class="text" style="text-anchor: start; font-size: 11px;">Docker: Fully containerized • Render: Free tier CI/CD • Railway: Git push deployment • Both support environment variables</text>
</svg>"""


def main() -> None:
    """Generate and save all diagrams."""
    diagrams_dir = Path(__file__).parent

    with open(diagrams_dir / "architecture.svg", "w") as f:
        f.write(generate_architecture_svg())

    with open(diagrams_dir / "deployment.svg", "w") as f:
        f.write(generate_deployment_svg())

    print("Generated architecture.svg and deployment.svg")


if __name__ == "__main__":
    main()
