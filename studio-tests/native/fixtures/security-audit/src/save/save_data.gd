extends Node
func load_slot(path: String) -> Dictionary:
    return JSON.parse_string(FileAccess.get_file_as_string(path))
