import json

def generate_mermaid_chart(graph_data):
    print("🎨 Formatting JSON graph structure into a stylized Mermaid.js chart...")
    
    if not graph_data:
        return "graph TD\n    Error[No Graph Data Available]"
    
    # Initialize a Top-Down (TD) graph
    mermaid_lines = ["graph TD"]
    
    # Track nodes that are involved in errors for styling later
    error_nodes = set()
    
    # If the global payload flagged a breaking change, highlight the main component
    has_global_error = graph_data.get("has_error", False)
    error_details = graph_data.get("error_details", "")
    
    # 1. Generate Nodes
    for node in graph_data.get("nodes", []):
        node_id = node.get("id").replace("/", "_").replace(".", "_") # Sanitize IDs for Mermaid syntax
        label = node.get("label")
        node_type = node.get("type", "file")
        
        # Format node shapes based on type
        if node_type == "file":
            mermaid_lines.append(f'    {node_id}["📄 {label}"]')
        elif node_type == "component":
            mermaid_lines.append(f'    {node_id}("(⚙️) {label}")')
        else:
            mermaid_lines.append(f'    {node_id}(["🔹 {label}"])')
            
        # If this is the broken component or a missing field, flag it
        if has_global_error and ("email" in node_id or "create_user" in node_id):
            error_nodes.add(node_id)

    mermaid_lines.append("") # Blank line for organization

    # 2. Generate Edges
    for edge in graph_data.get("edges", []):
        source_id = edge.get("source").replace("/", "_").replace(".", "_")
        target_id = edge.get("target").replace("/", "_").replace(".", "_")
        relationship = edge.get("relationship", "connects")
        
        mermaid_lines.append(f"    {source_id} -->|{relationship}| {target_id}")

    mermaid_lines.append("") # Blank line for styling rules

    # 3. Apply Custom Color Styling
    # Default successful/stable nodes: Soft Gray/Dark Outline
    mermaid_lines.append("    classDef stable fill:#e1f5fe,stroke:#03a9f4,stroke-width:2px,color:#000;")
    # Error/Broken nodes: Red/Alert styling
    mermaid_lines.append("    classDef broken fill:#ffebee,stroke:#ef5350,stroke-width:3px,color:#b71c1c,font-weight:bold;")
    
    # Assign classes to specific nodes
    all_node_ids = [n.get("id").replace("/", "_").replace(".", "_") for n in graph_data.get("nodes", [])]
    for n_id in all_node_ids:
        if n_id in error_nodes:
            mermaid_lines.append(f"    class {n_id} broken;")
        else:
            mermaid_lines.append(f"    class {n_id} stable;")

    # If there's an overarching error comment, add it as a floating note box
    if has_global_error and error_details:
        mermaid_lines.append(f'\n    ErrorNote["⚠️ CRITICAL ERROR:<br/>{error_details}"]')
        mermaid_lines.append("    style ErrorNote fill:#fff3e0,stroke:#ffb74d,stroke-width:2px,color:#e65100;")

    # Join lines together into a clean, complete code block string
    return "\n".join(mermaid_lines)

if __name__ == "__main__":
    # Import the exact output structure generated in Step 3
    sample_json_input = {
      "nodes": [
        {"id": "api/user.py", "label": "api/user.py", "type": "file"},
        {"id": "create_user", "label": "create_user", "type": "component"},
        {"id": "username", "label": "username", "type": "module"},
        {"id": "email", "label": "email", "type": "module"}
      ],
      "edges": [
        {"source": "api/user.py", "target": "create_user", "relationship": "contains"},
        {"source": "create_user", "target": "username", "relationship": "uses"},
        {"source": "create_user", "target": "email", "relationship": "uses"}
      ],
      "has_error": True,
      "error_details": "Removed email field in create_user function - breaking change"
    }
    
    mermaid_output = generate_mermaid_chart(sample_json_input)
    print("\n🚀 Generated Mermaid.js Source Syntax:")
    print("-" * 50)
    print(mermaid_output)
    print("-" * 50)
