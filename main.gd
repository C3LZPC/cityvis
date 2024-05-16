extends Node3D


const HTerrain = preload("res://addons/zylann.hterrain/hterrain.gd")
const HTerrainData = preload("res://addons/zylann.hterrain/hterrain_data.gd")

const max_threads = 25


var threads = []
var c_x = 0
var c_y = 0
var t_x = 0
var t_y = 0

@onready var tb = get_node("TerrainBase")
@onready var ui = get_node("GUI")
var height_offset = 0.0
var max_height = 0.0
var map_step = 512

func _load_map_from_thread(x : int, y : int, step_size : int, min_height : float, lmax_height : float, terrain : HTerrain):
	var data = HTerrainData.new()
	data.resize(step_size + 1)
	
	data._import_map(HTerrainData.CHANNEL_COLOR, "res://data/" + str(step_size) + "/" + str(x) + "_" + str(y) + "_color.png")
	data._import_heightmap("res://data/" + str(step_size) + "/" + str(x) + "_" + str(y) + "_height.png", 0.0, lmax_height - min_height, false)
	
	'''
	var hmap : Image = data.get_image(HTerrainData.CHANNEL_HEIGHT)
	var normal_map = data.get_image(HTerrainData.CHANNEL_NORMAL)
	for a in hmap.get_width():
		for b in hmap.get_height():
			var h = hmap.get_pixel(a, b).r
			var h_r = hmap.get_pixel(a + 1, b).r
			var h_f = hmap.get_pixel(a, b + 1).r
			var n = Vector3(h - h_r, 0.1, h_f - h).normalized()
			normal_map.set_pixel(a, b, HTerrainData.encode_normal(n))
	'''
	
	call_deferred("_loading_done", terrain, data)

func _loading_done(terrain : HTerrain, data : HTerrainData):
	terrain.set_data(data)
	ui.update_progressbar()

func _process(_delta):
	var finished_threads = []
	for t : Thread in threads:
		if not t.is_alive():
			t.wait_to_finish()
			finished_threads.append(t)
	for t : Thread in finished_threads:
		threads.erase(t)
	
	if c_x < t_x or c_y < t_y:
		if threads.size() < max_threads:
			var terrain = HTerrain.new()
			get_node("TerrainBase").add_child(terrain)
			terrain.translate(Vector3(c_y * 0.5 * map_step, height_offset, c_x * 0.5 * map_step))
			terrain.name = str(c_x) + "_" + str(c_y)
			terrain.scale = Vector3(0.5, 1, 0.5)
			#terrain.set_shader_type(HTerrain.SHADER_LOW_POLY)
			terrain.set_shader_type(HTerrain.SHADER_MULTISPLAT16)
			terrain.lod_scale = 12.0 # 8.0
			
			var t = Thread.new()
			while t.start(_load_map_from_thread.bind(c_x, c_y, map_step, height_offset, max_height, terrain)) != OK:
				t = Thread.new()
			threads.append(t)
			c_y += 1
	
	if c_y >= t_y:
		c_y -= t_y
		c_x += 1
	
	if c_x >= t_x:
		self.set_process(false)

func _ready():
	get_node("Camera3D").ui = ui
	
	for c in tb.get_children():
		c.queue_free()
	
	var map_metadata = JSON.parse_string(FileAccess.get_file_as_string("res://data/" + str(map_step) + "/metadata.json"))
	if map_metadata:
		height_offset = map_metadata["min_height"]
		max_height = map_metadata["max_height"]
		#var map_max_x = 5
		#var map_max_y = 5
		var map_max_x = int(map_metadata["x"])
		var map_max_y = int(map_metadata["y"])
		t_x = map_max_x
		t_y = map_max_y
		
		get_node("Camera3D").translate(Vector3(map_max_y * 0.5 * 0.5 * map_step, 0, map_max_x * 0.5 * 0.5 * map_step))
		
		ui.set_map_extents(map_max_y * 0.5 * map_step, 1000, map_max_x * 0.5 * map_step)
		ui.reset_progressbar(map_max_x * map_max_y)
