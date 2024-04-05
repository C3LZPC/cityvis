extends Camera3D

const mouse_sensitivity = 0.1

var v = Vector3()
var is_scanning_mouse = true

var ui = null

func _ready():
	self.near = 0.1
	self.far = 100000
	
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	is_scanning_mouse = true

func _process(_delta):
	rotation_degrees.x = v.x
	rotation_degrees.y = v.y
	
	var mul = 1
	if Input.is_key_pressed(KEY_SPACE):
		mul = 10
	
	if Input.is_key_pressed(KEY_E):
		translate(Vector3.UP * mouse_sensitivity * mul)
	if Input.is_key_pressed(KEY_Q):
		translate(Vector3.DOWN * mouse_sensitivity * mul)
	if Input.is_key_pressed(KEY_W):
		translate(Vector3.FORWARD * mouse_sensitivity * mul)
	if Input.is_key_pressed(KEY_S):
		translate(Vector3.BACK * mouse_sensitivity * mul)
	if Input.is_key_pressed(KEY_A):
		translate(Vector3.LEFT * mouse_sensitivity * mul)
	if Input.is_key_pressed(KEY_D):
		translate(Vector3.RIGHT * mouse_sensitivity * mul)
	
	if ui != null:
		ui.update_position(self.position)

func _input(event):
	if is_scanning_mouse and event is InputEventMouseMotion:
		v.x -= event.relative.y * mouse_sensitivity
		v.y -= event.relative.x * mouse_sensitivity
		v.x = clamp(v.x, -80, 80)
	
	if event is InputEventKey:
		if not event.is_echo() and event.pressed:
			
			if event.keycode == KEY_SHIFT or event.keycode == KEY_ESCAPE:
				if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
					Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
					is_scanning_mouse = false
				elif Input.mouse_mode == Input.MOUSE_MODE_VISIBLE:
					Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
					is_scanning_mouse = true


