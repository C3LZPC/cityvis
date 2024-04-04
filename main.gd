extends Node3D


const HTerrain = preload("res://addons/zylann.hterrain/hterrain.gd")
const HTerrainData = preload("res://addons/zylann.hterrain/hterrain_data.gd")


var threads = {}
var height_offset = 0.0
var map_step = 512

func _load_map_from_thread(x : int, y : int, step_size : int, t : HTerrain):
	var data = HTerrainData.new()
	data._locked = true
	data.resize(513)
	data._import_map(HTerrainData.CHANNEL_COLOR, "res://data/" + str(step_size) + "/" + str(x) + "_" + str(y) + "_color.png")
	data._import_heightmap("res://data/" + str(step_size) + "/" + str(x) + "_" + str(y) + "_height.png", 0.0, 256.0, false)
	
	call_deferred("_loading_done", x, y, t, data)

func _loading_done(x : int, y : int, terrain : HTerrain, data : HTerrainData):
	print(str(x) + ", " + str(y) + " finished!")
	var t : Thread = threads[x][y]
	t.wait_to_finish()
	
	terrain.set_data(data)

func _ready():
	
	var tb = get_node("TerrainBase")
	
	for c in tb.get_children():
		c.queue_free()
	
	var map_metadata = JSON.parse_string(FileAccess.get_file_as_string("res://data/" + str(map_step) + "/metadata.json"))
	if map_metadata:
		height_offset = map_metadata["min_height"]
		var map_max_x = 5
		var map_max_y = 5
		#var map_max_x = int(map_metadata["x"])
		#var map_max_y = int(map_metadata["y"])
		
		get_node("Camera3D").translate(Vector3(map_max_y * 0.5 * 0.5 * map_step, 0, map_max_x * 0.5 * 0.5 * map_step))
		
		for x in map_max_x:
			threads[x] = {}
			for y in map_max_y:
				var terrain = HTerrain.new()
				get_node("TerrainBase").add_child(terrain)
				terrain.translate(Vector3(y * 0.5 * map_step, height_offset, x * 0.5 * map_step))
				terrain.name = str(x) + "_" + str(y)
				terrain.scale = Vector3(0.5, 1, 0.5)
				#terrain.centered = true
				terrain.set_shader_type(HTerrain.SHADER_LOW_POLY)
				
				
				#TODO: limit number of threads based on hardware capabilities
				var t = Thread.new()
				while t.start(_load_map_from_thread.bind(x, y, map_step, terrain)) != OK:
					t = Thread.new()
				threads[x][y] = t


