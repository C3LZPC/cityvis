extends CanvasLayer



func _ready():
	#TODO:
	pass

func printable_num(n : int) -> String:
	var i = 0.0
	var postfix = " B"
	
	if n / (1024 ** 1) > 1:
		i = n / (1024 ** 1)
		postfix = " KB"
	if n / (1024 ** 2) > 1:
		i = n / (1024 ** 2)
		postfix = " MB"
	if n / (1024 ** 3) > 1:
		i = n / (1024 ** 3)
		postfix = " GB"
	if n / (1024 ** 4) > 1:
		i = n / (1024 ** 4)
		postfix = " TB"
	
	return "%10.3f" % i + postfix

func _process(delta):
	get_node("Mertrics/MetricsContainer/FPS").text = "FPS: %10.2f" % Engine.get_frames_per_second()
	var mem = OS.get_memory_info()
	get_node("Mertrics/MetricsContainer/Mem").text = "RAM: " + printable_num(mem["free"]) + " / " + printable_num(mem["available"])
