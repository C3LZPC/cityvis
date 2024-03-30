extends Node3D


const HTerrain = preload("res://addons/zylann.hterrain/hterrain.gd")
const HTerrainData = preload("res://addons/zylann.hterrain/hterrain_data.gd")

func _ready():
	var terrain : HTerrain = get_node("HTerrain")
	var data = terrain.get_data()
	data.resize(513)
	
	data._import_map(HTerrainData.CHANNEL_COLOR, "res://data/513/0_16_color.png")
	data._import_heightmap("res://data/513/0_16_height.png", 0.0, 256.0, false)
	#data.notify_full_change() # function buggy, only works if ALL possible maps are present
	var rect = Rect2(0, 0, data.get_resolution(), data.get_resolution())
	data.notify_region_change(rect, HTerrainData.CHANNEL_COLOR, 0)
	data.notify_region_change(rect, HTerrainData.CHANNEL_HEIGHT, 0)
	#data.notify_region_change(rect, HTerrainData.CHANNEL_NORMAL, 0)
	
	terrain.set_shader_type(HTerrain.SHADER_LOW_POLY)
	terrain.set_map_scale(Vector3(0.5, 1, 0.5))
