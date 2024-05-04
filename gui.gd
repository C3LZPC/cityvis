extends CanvasLayer

const diamond_material = preload("res://diamond_material.tres")

var load_progress = 0
var menu_open = false

var cam = null

func printable_num(n : int) -> String:
	var i = 0.0
	var postfix = " B"
	
	if float(n) / (1024 ** 1) > 1:
		i = float(n) / (1024 ** 1)
		postfix = " KB"
	if float(n) / (1024 ** 2) > 1:
		i = float(n) / (1024 ** 2)
		postfix = " MB"
	if float(n) / (1024 ** 3) > 1:
		i = float(n) / (1024 ** 3)
		postfix = " GB"
	if float(n) / (1024 ** 4) > 1:
		i = float(n) / (1024 ** 4)
		postfix = " TB"
	
	return "%10.3f" % i + postfix

func _ready():
	get_node("Pause/Box/Quit").connect("pressed", self.quit)
	
	get_node("ColorRect").material = diamond_material
	get_node("Pause").hide()
	get_node("Pos").hide()
	get_node("LoadProgress").show()

func _process(_delta):
	get_node("Mertrics/MetricsContainer/FPS").text = "FPS: %10.2f" % Engine.get_frames_per_second()
	var mem = OS.get_memory_info()
	#get_node("Mertrics/MetricsContainer/Mem").text = "RAM: " + printable_num(mem["free"]) + " / " + printable_num(mem["available"])
	get_node("Mertrics/MetricsContainer/Mem").text = "RAM: " + printable_num(mem["free"]) + " / " + printable_num(mem["physical"])

func _input(event):
	if event is InputEventKey and event.is_pressed():
		if event.keycode == KEY_ESCAPE:
			menu_open = !menu_open
			
			if menu_open:
				get_node("Pause").show()
				cam.set_process(false)
				cam.is_mouse_lockable = false
			else:
				get_node("Pause").hide()
				cam.set_process(true)
				cam.is_mouse_lockable = true

func update_position(pos : Vector3) -> void:
	get_node("Pos/PosContainer/Pos").text = "X: %10.2f " % pos.x + "Y: %10.2f " % pos.y + "Z: %10.2f" % pos.z

func reset_progressbar(max_num : int) -> void:
	load_progress = 0
	get_node("LoadProgress/LoadProgressContainer/Label").text = "0 / %d" % max_num
	var pb : ProgressBar = get_node("LoadProgress/LoadProgressContainer/Progress")
	pb.min_value = 0
	pb.max_value = max_num
	pb.value = load_progress
	get_node("Pos").hide()
	get_node("LoadProgress").show()

func update_progressbar() -> void:
	load_progress += 1
	var pb : ProgressBar = get_node("LoadProgress/LoadProgressContainer/Progress")
	pb.value = load_progress
	get_node("LoadProgress/LoadProgressContainer/Label").text = "%d " % pb.value + "/ %d" % pb.max_value
	if pb.value == pb.max_value:
		self.progressbar_done()

func progressbar_done() -> void:
	var tw = get_tree().create_tween()
	#tw.set_trans(Tween.TRANS_CUBIC)
	tw.set_trans(Tween.TRANS_QUAD)
	#tw.set_ease(Tween.EASE_OUT)
	tw.parallel().tween_property(diamond_material, "shader_parameter/progress", 1, 2)
	tw.parallel().tween_property(get_node("LoadProgress"), "modulate:a", 0.0, 2)
	tw.chain().tween_callback(progressbar_done2)

func progressbar_done2() -> bool:
	get_node("LoadProgress").hide()
	get_node("LoadProgress").modulate.a = 1.0
	get_node("Pos").show()
	return true

func quit():
	get_tree().quit()
