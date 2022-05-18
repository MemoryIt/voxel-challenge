from scene import Scene; import taichi as ti
from taichi.math import *
ti.init(arch=ti.gpu)
scene = Scene(voxel_edges=0,exposure=20)
scene.set_floor(-1, (1.0, 1.0, 1.0))
def R0(s):
	m=s[27],s[24],s[21],s[54],s[51],s[48],s[39],s[42],s[45],s[34],s[31],s[28],s[35],s[29],s[36],s[33],s[30],s[9],s[6],s[3]
	s[3],s[6],s[9],s[27],s[24],s[21],s[54],s[51],s[48],s[36],s[35],s[34],s[33],s[31],s[30],s[29],s[28],s[45],s[42],s[39]=m
	return(s)
def R1(s):
	m=s[10],s[13],s[16],s[11],s[17],s[12],s[15],s[18],s[37],s[40],s[43],s[1],s[4],s[7],s[25],s[22],s[19],s[46],s[49],s[52]
	s[12],s[11],s[10],s[15],s[13],s[18],s[17],s[16],s[1],s[4],s[7],s[25],s[22],s[19],s[52],s[49],s[46],s[43],s[40],s[37]=m
	return(s)
def R2(s):
	m=s[7],s[4],s[1],s[8],s[2],s[9],s[6],s[3],s[25],s[26],s[27],s[36],s[33],s[30],s[45],s[44],s[43],s[12],s[15],s[18]
	s[1],s[2],s[3],s[4],s[6],s[7],s[8],s[9],s[12],s[15],s[18],s[25],s[26],s[27],s[36],s[33],s[30],s[45],s[44],s[43]=m
	return(s)
def R3(s):
	a=s[39],s[38],s[37],s[10],s[13],s[16],s[19],s[20],s[21],s[34]
	b=s[31],s[28],s[46],s[49],s[52],s[47],s[53],s[48],s[51],s[54]
	s[10],s[13],s[16],s[19],s[20],s[21],s[34],s[31],s[28],s[39]=a
	s[38],s[37],s[52],s[53],s[54],s[49],s[51],s[46],s[47],s[48]=b
	return(s)
def R4(s):
	m=s[16],s[17],s[18],s[52],s[19],s[22],s[25],s[7],s[53],s[20],s[26],s[8],s[54],s[21],s[24],s[27],s[9],s[34],s[35],s[36]
	s[7],s[8],s[9],s[18],s[25],s[26],s[27],s[36],s[17],s[22],s[24],s[35],s[16],s[19],s[20],s[21],s[34],s[52],s[53],s[54]=m
	return(s)
def R5(s):
	m=s[30],s[29],s[28],s[3],s[48],s[39],s[42],s[45],s[2],s[47],s[38],s[44],s[1],s[46],s[37],s[40],s[43],s[12],s[11],s[10]
	s[1],s[2],s[3],s[12],s[30],s[45],s[44],s[43],s[11],s[29],s[42],s[40],s[10],s[28],s[39],s[38],s[37],s[46],s[47],s[48]=m
	return(s) 
def get_state(p):
	s=[0]+9*[1]+[n*2 for n in 9*[1]]+[n*3 for n in 9*[1]]+[n*5 for n in 9*[1]]+[n*4 for n in 9*[1]]+[n*6 for n in 9*[1]]
	for m in p:
		s=eval('R'+m)(s)
	return s
def get_random_state(my_seed):
	return get_state([str((ord(n)-48)%6) for n in str(hash(my_seed))[1:]])
@ti.func
def create_block(code, s, c, ct,cc,lt,lc,surface_voxel_type,surface_voxel_color):  
	O=(16+ivec3((3*s[0]+4)*(s[0]>0),(3*s[1]+4)*(s[1]>0),(3*s[2]+4)*(s[2]>0)))*code
	S=ivec3((3*s[0]+4)*(s[0]>0),(3*s[1]+4)*(s[1]>0),(3*s[2]+4)*(s[2]>0))+(1-ti.abs(code))*15
	for x, y, z in ti.ndrange((O[0]-S[0],O[0]+S[0]+1),(O[1]-S[1],O[1]+S[1]+1),(O[2]-S[2],O[2]+S[2]+1)):
		scene.set_voxel(vec3(x, y, z), ct, cc)
		if ((ti.abs(x-O[0])==S[0])+(ti.abs(y-O[1])==S[1])+(ti.abs(z-O[2])==S[2]))>=2:
			scene.set_voxel(vec3(x, y, z), lt, lc)
		if ((x-O[0])==(code[0]*S[0]))and(ti.abs(y-O[1])+2<S[1])and(ti.abs(z-O[2])+2<S[2])and(c[0]!=0):
			scene.set_voxel(vec3(x, y, z), surface_voxel_type, vec3(1-c[0]/6,(c[0]%2)/2+c[0]/12,c[0]/6))
		elif (ti.abs(x-O[0])+2<S[0])and((y-O[1])==(code[1]*S[1]))and(ti.abs(z-O[2])+2<S[2])and(c[1]!=0):
			scene.set_voxel(vec3(x, y, z), surface_voxel_type, vec3(1-c[1]/6,(c[1]%2)/2+c[1]/12,c[1]/6))
		elif (ti.abs(x-O[0])+2<S[0])and(ti.abs(y-O[1])+2<S[1])and((z-O[2])==(code[2]*S[2]))and(c[2]!=0):
			scene.set_voxel(vec3(x, y, z), surface_voxel_type, vec3(1-c[2]/6,(c[2]%2)/2+c[2]/12,c[2]/6))
@ti.kernel
def initialize_voxels(a:ti.i32,b:ti.i32,c:ti.i32, d:ti.i32,e:ti.i32,f:ti.i32, g:ti.i32,h:ti.i32,i:ti.i32,\
					  j:ti.i32, k:ti.f32,l:ti.f32,m:ti.f32, n:ti.i32, o:ti.f32,p:ti.f32,q:ti.f32, r:ti.i32):
	create_block(ivec3(a,b,c),ivec3(d,e,f),ivec3(g,h,i),j,vec3(k,l,m),n,vec3(o,p,q),r,vec3(1,1,1))
def my_cube(t,d,p,ct,cr,cg,cb,lt,lr,lg,lb,st):
	s=(t%2)*eval(d[0].isalpha()*'get_random_state'+(not d[0].isalpha())*'get_state')(d)+((t+1)%2)*([0]+54*[4])
	c=(t>1)*eval(p[0].isalpha()*'get_random_state'+(not p[0].isalpha())*'get_state')(p)+(not (t>1))*(55*[0])
	initialize_voxels(0,0,0, 14,14,14, 3,3,3, 0, 1,1,1, 2,0.5,0.5,0.5, 0)
	for i in range(27):
		x,y,z=i//9-1,(i%9)//3-1,(i%9)%3-1
		u,v,w=(9*(x+2)+5+3*z+y)*abs(x),int(45*(1-y)/2+5+3*z+x)*abs(y),(9*(3-z)+5+3*y+x)*abs(z)
		initialize_voxels(x,y,z,s[u],s[v],s[w],c[u],c[v],c[w],ct,cr,cg,cb,lt,lr,lg,lb,st) 
my_cube(3,'050322144255145','3141525', 0, 0.3,0.3,0.3, 0, 0,0,0, 1)
scene.finish()