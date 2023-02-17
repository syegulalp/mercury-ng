def upload_script(
    upload_path = None,
    upload_file_path = None,
    editor_css = None,
    refresh_media=False,
    drop_js = True):
    
    script = []

    if upload_path:
        script.append(f'var upload_path = "{upload_path}";')
    if upload_file_path:
        script.append(f'var uploadFilePath = "{upload_file_path}";')
    if editor_css:
        script.append(f'var alt_editor_css = "{editor_css},";')
    if refresh_media:
        script.append("function refreshMediaList(){{}};")
    
    script = ["<script>"] + script + ["</script>"]

    if drop_js:
        script.append('<script src="/static/js/drop.js"></script>')
    
    return "\n".join(script)    