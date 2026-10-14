from pathlib import Path

target_file = Path("src/fao_transactions/visualization/map_builder.py")
content = target_file.read_text(encoding="utf-8")

old_func = """  function formatMarkdownSimple(text) {
    if (!text) return '';
    let out = text
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/### (.*)/g, '<div style="font-weight:800; font-size:13px; color:#C9A24D; margin:6px 0 4px 0;">$1</div>')
      .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
      .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
      .replace(/- (.*)/g, '<div style="margin-left:8px; display:flex; gap:6px;"><span style="color:#C9A24D;">•</span><span>$1</span></div>')
      .replace(/\\n\\n/g, '<div style="height:6px;"></div>')
      .replace(/\\n/g, '<br/>');
    return out;
  }"""

new_func = """  function formatMarkdownSimple(text) {
    if (!text) return '';
    var lines = text.split('\\n');
    var out = [];
    for (var i = 0; i < lines.length; i++) {
      var l = lines[i];
      if (l.indexOf('### ') === 0) {
        out.push('<div style="font-weight:800; font-size:13px; color:#C9A24D; margin:8px 0 4px 0;">' + l.substring(4) + '</div>');
      } else if (l.indexOf('- ') === 0) {
        out.push('<div style="margin-left:8px; display:flex; gap:6px; margin-bottom:2px;"><span style="color:#C9A24D;">•</span><span>' + l.substring(2) + '</span></div>');
      } else if (l.indexOf('> ') === 0) {
        out.push('<div style="border-left:2px solid #C9A24D; padding-left:8px; color:#94a3b8; font-style:italic; margin:4px 0;">' + l.substring(2) + '</div>');
      } else if (!l.trim()) {
        out.push('<div style="height:6px;"></div>');
      } else {
        out.push('<div>' + l + '</div>');
      }
    }
    return out.join('');
  }"""

# Try exact match or line-by-line replace
if "function formatMarkdownSimple(text) {" in content:
    start_idx = content.find("  function formatMarkdownSimple(text) {")
    end_idx = content.find("  }\n\n\n</script>", start_idx)
    if end_idx == -1:
        end_idx = content.find("  }\r\n\r\n\r\n</script>", start_idx)
    if end_idx != -1:
        content = content[:start_idx] + new_func + content[end_idx+3:]
        target_file.write_text(content, encoding="utf-8")
        print("Successfully replaced formatMarkdownSimple!")
    else:
        print("Could not find end index")
else:
    print("Function not found")
