import pygame
import random
import time
import json

pygame.init()
PANTALLA_ANCHO=800
PANTALLA_ALTO=900
VOLUMEN = 1
DEBUG=0
GAME_VERSION = "1.00"


MATRIZ = [11,[["C0"],["C1"],["C1"],["P"],["P"]]]

window = pygame.display.set_mode((PANTALLA_ANCHO,PANTALLA_ALTO))
pygame.display.set_caption(f"Space Invaders  v{GAME_VERSION}  |  kelus")

pygame.display.set_icon(pygame.image.load("assets/sprites/icon.png"))

fuente=pygame.font.Font(("assets/fuente.ttf"),25)

visual = json.loads(open("assets/traducciones.json","r").read())
idiomas = ['es','en','fr','de','it','pt']
idioma = 0


print("\nGAME INSPIRED IN SPACE INVADERS FROM 1978. GAME DEVELOPED BY KELUS - Hugo Moreda")
print("IMPORTANT: GAME SHOULD RUN AROUND  40-50 FPS TO WORK PROPERLY\n")

def visual_puntos(cantidad):
    return str(cantidad).zfill(4)


#C0 - Calamar
#C1 - Cangrejo
#P - Pulpo
escalado_sprite=2.25*2
sprites={
    #"sprite_name" : [ [width,height] , [frame0:[x coord on file,y coord on file],frame1:...] ]
    "C0":[[8,8],[[0,25],[8,25],[16,25]]],
    "C1":[[11,8],[[0,33],[11,33],[22,33]]],
    "P":[[12,8],[[0,41],[12,41],[24,41]]],
    "UFO":[[32,14],[[0,49]]],
    "explosion":[[12,8],[[24,25]]],
    "jugador_HUD":[[15,10],[[15,63]]],
    "bandera":[[25,25],[[0,0],[25,0],[50,0],[50,49],[50,74],[25,74]]],
    "jugador":[[15,10],[[0,63],[15,63]]],
    "disparo":[[3,8],[[8,89],[11,89]]],
    "disparo_explosion":[[8,8],[[14,89],[0,89]]],
    "obstaculo":[[21,16],[[0,73]]],
    "volumen":[[13,11],[[49,25],[62,25]]]
}
puntos={
    "C0":30,
    "C1":20,
    "P":10,
    "UFO":[50,100,150,300]
}

def trad(identificador, _idioma):
    global idiomas
    return visual[idiomas[_idioma]][identificador]


class Spritesheet:
    def __init__(self,nombre_archivo):
        self.archivo=nombre_archivo
        self.sheet=pygame.image.load(self.archivo).convert()

    def conseguir_sprite(self,x,y,w,h,cambiarColor,tipo,escala=1):
        sprite=pygame.Surface((w,h))
        sprite.set_colorkey((0,0,0))
        sprite.blit(self.sheet,(0,0),(x,y,w,h))
        sprite=pygame.transform.scale(sprite,(w*escalado_sprite*escala,h*escalado_sprite*escala))

        if cambiarColor is True:
            if tipo=="C1":
                var=pygame.PixelArray(sprite)
                var.replace((252,252,252),(66,233,244))
                var.replace((255,255,255),(66,233,244))
                del var
            elif tipo=="C0":
                var=pygame.PixelArray(sprite)
                var.replace((252,252,252),(219,85,221))
                var.replace((255,255,255),(219,85,221))
                del var
            elif tipo=="P":
                var=pygame.PixelArray(sprite)
                var.replace((252,252,252),(235,223,100))
                var.replace((255,255,255),(235,223,100))
                del var

        return sprite
_nombre = 'sprites.png'
mis_sprites=Spritesheet(f'assets/sprites/{_nombre}')

def cargarSprites():
    global _nombre
    nombres_sprites=list(sprites)
    print(f"#### LOADED SPRITES ({_nombre}):")
    for i in range(len(sprites)):
        nombre = nombres_sprites[i]
        dimensiones=sprites[nombre][0]
        frames_cantidad = len(sprites[nombre][1])
        print(f"\n     Nombre: {nombre} | Dimensiones: {dimensiones} | Frames:",end="")
        for i in range(frames_cantidad):
            coord_frame=sprites[nombre][1][i]
            print(f"    {i+1}: {coord_frame}", end="")

cargarSprites()

BORDES_PANTALLA = [100,PANTALLA_ALTO-50]
rect_BORDES_PANTALLA = [pygame.Rect(0,BORDES_PANTALLA[0],PANTALLA_ANCHO,2),pygame.Rect(0,BORDES_PANTALLA[1],PANTALLA_ANCHO,2)]

window.fill((0,0,0))
celdas = []



BLANCO=(255,255,255)
NEGRO=(0,0,0)
ROJO=(238,67,73)
def tocar_sonido(sonido):
    global VOLUMEN
    sonidos = {"jugador_disparo":"disparo","matar_enemigo":"enemigo_matado","jugador_disparado":"explosion","boton":"select"}
    if VOLUMEN != 0:
        pygame.mixer.Sound("assets/sonidos/"+sonidos[sonido]+".wav").play()



def idx(i,j,filas,columnas):
    return (j+i*columnas)

class grupo_enemigos:
    def __init__ (self, matrizEnemigos,mostrarFondo,pixelesMovimiento):
        self.filas = len(matrizEnemigos[1])
        self.columnas = matrizEnemigos[0]
        self.aliensPfila=matrizEnemigos[0]
        matrizEnemigos= matrizEnemigos[1]
        self.aliens=[]
        self.mostrarFondo=mostrarFondo

        self.pixelesMovimiento = pixelesMovimiento

        self.movimiento_derecha=True
        self.movimiento_izquierda=False
        self.tipo="grupo_enemigos"

        self.aliens = []
        self.alien_anchura_max = 0
        alturasAliens=0
        for fila in range(self.filas):
            for col in range(self.columnas):
                tipo = matrizEnemigos[fila][0]
                anchura = sprites[tipo][0][0]
                altura = sprites[tipo][0][1]
                if col==0:
                    alturasAliens+=altura
                if anchura>self.alien_anchura_max:
                    self.alien_anchura_max=anchura
                self.aliens.append(Alien((255,0,0),tipo))
        self.alien_anchura_max *= escalado_sprite

        self.separacion_horizontal_aliens = ((PANTALLA_ANCHO - (self.aliensPfila * self.alien_anchura_max))/self.aliensPfila)/2

        self.anchura_bloque = self.aliensPfila * self.alien_anchura_max + self.separacion_horizontal_aliens * self.aliensPfila - self.separacion_horizontal_aliens
        self.altura_bloque = alturasAliens * escalado_sprite + 15 * (self.filas-1)

        self.x=(PANTALLA_ANCHO - self.anchura_bloque)/2
        self.y=200

        self.quitadas = [False for i in range(self.columnas)]

        self.mas_baja = 0


    def mostrar(self):
        if self.mostrarFondo is True:
            pygame.draw.rect(window,(255,0,0),pygame.Rect(self.x,self.y,self.anchura_bloque,self.altura_bloque))
        for fila in range(self.filas):
            for col in range(self.columnas):
                self.aliens[idx(fila,col,self.filas,self.columnas)].dibujar(fila,col,self.x,self.y,self.aliensPfila,self.alien_anchura_max)




        for col in range(self.columnas):
            cantidad_vert = 0
            for fila in range(self.filas):
                if self.aliens[idx(fila,col,self.filas,self.columnas)].explotado == False:
                    cantidad_vert+=1


            if cantidad_vert==0 and self.quitadas[col]==False:
                self.quitadas[col]=True
                print(f"columna {cantidad_vert} eliminada")
        if enemigosConVida()!=0:
            for fila in range(self.filas):
                qtt = 0
                for col in range(self.columnas):
                    if self.aliens[idx(fila,col,self.filas,self.columnas)].explotado == False:
                        qtt+=1
                if qtt>0:
                    vertical_mas_baja = fila


            self.mas_baja = self.y + 8 * escalado_sprite * self.filas + 25 * (self.filas-1) - 25 ##quitamos el ultimo espacio


            dif = self.filas-vertical_mas_baja-1
            self.mas_baja -= dif * 8 * escalado_sprite + (dif-1) * 25








    def mover(self):
        global obstaculos0, jugador0
        #actualizar todos los frames

        cantidad_izq = 0
        cantidad_der = 0

        for i in range(self.columnas):
            if self.quitadas[i]==False:
                break
            cantidad_izq+=1

        for i in reversed(range(self.columnas)):
            if self.quitadas[i]==False:
                break
            cantidad_der+=1
        #print(f"{cantidad_izq},{cantidad_der}")

        vert = 25

        for fila in range(self.filas):
            for col in range(self.columnas):
                self.aliens[idx(fila,col,self.filas,self.columnas)].cambiar_frame()

        diferencia=self.pixelesMovimiento
        if self.movimiento_derecha==True:
            if not(self.x+diferencia+self.anchura_bloque - (cantidad_der * (self.alien_anchura_max  + self.separacion_horizontal_aliens)) > PANTALLA_ANCHO):
                self.x+=diferencia
            else:
                self.y+=vert
                self.movimiento_derecha=False
                self.movimiento_izquierda=True
                self.mover()
        elif self.movimiento_izquierda==True:
            if not(self.x-diferencia + (cantidad_izq * (self.alien_anchura_max + self.separacion_horizontal_aliens)) < 0):
                self.x-=diferencia
            else:
                self.y+=vert
                self.movimiento_derecha=True
                self.movimiento_izquierda=False
                self.mover()

        ########## comprobar colision de obstaculos y aliens, si es asi se borran
        for j in range(len(obstaculos0.obstaculos)):
            for k in range(len(obstaculos0.obstaculos[j].rect)):
                for i in range(len(self.aliens)):
                    rect=self.aliens[i].rect
                    if obstaculos0.obstaculos[j].rect[k].colliderect(rect) is True and self.aliens[i].vida is True:
                        print(f"Obstaculo {j} eliminado")
                        obstaculos0.obstaculos[j].vida = 0
        for i in range(len(self.aliens)):
            rect = self.aliens[i].rect
            for j in range(len(jugador0.rect)):
                if jugador0.rect[j].colliderect(rect) is True and self.aliens[i].vida is True:
                    jugador0.vidas = 0


    def conseguir_aliens_vivos(self):
        _aliens_vivos = []
        for i in range(0,len(self.aliens)):
            for i in range(len(self.aliens)):
                if self.aliens[i].vida is True:
                    _aliens_vivos.append(self.aliens[i])
        return _aliens_vivos

    def disparar(self):
        aliensvivos=enemigosConVida()

        if aliensvivos==1:
            if not balas_enemigo:
                aliens_vivos = self.conseguir_aliens_vivos()
                num=0
                bala_nueva = Bala(False,aliens_vivos[num],False)
                balas_enemigo.append(bala_nueva)

        elif aliensvivos>1:
            aliens_vivos = self.conseguir_aliens_vivos()

            if len(balas_enemigo)==1:
                num=random.randint(0,len(aliens_vivos))
                bala_nueva = Bala(False,aliens_vivos[num-2],False)
                balas_enemigo.append(bala_nueva)

            elif not balas_enemigo:
                for i in range(0,2):
                    num=random.randint(0,len(aliens_vivos))
                    bala_nueva = Bala(False,aliens_vivos[num-1],False)
                    balas_enemigo.append(bala_nueva)








class Alien:
    def __init__ (self,color,tipo):
        self.color = color
        self.vida = True
        self.tipo = tipo

        self.anchura=sprites[self.tipo][0][0]*escalado_sprite
        self.altura =sprites[self.tipo][0][1]*escalado_sprite

        self.rect = pygame.Rect(0,0,self.anchura,self.altura)

        self.frames = sprites[self.tipo][1]
        self.cantidad_frames = len(self.frames)

        self.dimensiones_explosion = sprites['explosion'][0]
        self.frame_explosion = sprites['explosion'][1][0]

        self.x_disparo=30
        self.y_disparo=30

        self.momento_explosion=-1
        self.explotado=False

        self.frame_actual=0

    def cambiar_frame(self):
        if self.frame_actual==0 or self.frame_actual==2:
            self.frame_actual=1
        elif self.frame_actual==1:
            self.frame_actual=0
    def dibujar(self,fila,columna,x_grupo,y_grupo,cantidadPorFila,alienAnchuraMaxima):
        separacion_vertical=25
        separacion_horizontal = ((PANTALLA_ANCHO - (cantidadPorFila * alienAnchuraMaxima))/cantidadPorFila)/2
        diferencia=alienAnchuraMaxima-self.anchura

        if self.tipo=="P":
            x=columna*self.anchura+separacion_horizontal*columna+x_grupo
        else: x=columna*self.anchura + diferencia/2 + diferencia*columna+separacion_horizontal*columna+x_grupo

        y=fila*self.altura+separacion_vertical*fila+y_grupo
        self.rect = pygame.Rect(x,y,self.anchura,self.altura)
        if self.vida is True:
            #pygame.draw.rect(window,self.color,self.rect)

            self.x_disparo=x+self.anchura/2
            self.y_disparo=y+self.altura-10

            sprite=mis_sprites.conseguir_sprite(self.frames[self.frame_actual][0],self.frames[self.frame_actual][1],self.anchura/escalado_sprite,self.altura/escalado_sprite, True,self.tipo)
            window.blit(sprite,(x,y))
        elif self.vida is False:
            if self.explotado is False:
                if self.momento_explosion==-1:
                        self.momento_explosion=time.time()
                        sprite = mis_sprites.conseguir_sprite(self.frame_explosion[0],self.frame_explosion[1],self.dimensiones_explosion[0],self.dimensiones_explosion[1], True, self.tipo)
                        window.blit(sprite,(x,y))

                elif (time.time()-self.momento_explosion)<0.1:
                        sprite = mis_sprites.conseguir_sprite(self.frame_explosion[0],self.frame_explosion[1],self.dimensiones_explosion[0],self.dimensiones_explosion[1], True,self.tipo)
                        window.blit(sprite,(x,y))
                elif (time.time()-self.momento_explosion)>0.1:
                    self.explotado=True
        #pygame.draw.circle(window,(255,0,0),(self.x_disparo,self.y_disparo),5)

def limpiar():
    window.fill((0,0,0))


class Jugador():
    def __init__ (self):
        self.anchura=15 * escalado_sprite
        self.altura= 10  * escalado_sprite

        self.color=(98,222,109)
        self.posicion_central()

        self.vidas=3
        self.vivo=True

        self.puntos=0

        self.frame_actual = 0

        self.tecla_levantada = True



        self.disparoHabilitado=True

        self.tipo="jugador"
        self.rect=[None,None]

    def posicion_central(self):
        self.x=PANTALLA_ANCHO/2-self.anchura/2
        self.y=PANTALLA_ALTO-75
        self.x_disparo=self.x+self.anchura/2
        self.y_disparo=self.y+20

    def dibujar(self):
        dimensiones_jugador = sprites['jugador'][0]
        frame_jugador = sprites['jugador'][1][self.frame_actual]
        sprite = mis_sprites.conseguir_sprite(frame_jugador[0],frame_jugador[1],dimensiones_jugador[0],dimensiones_jugador[1], True, self.tipo)
        window.blit(sprite,(self.x,self.y))



        self.rect[0]=pygame.Rect(self.x,self.y+18,self.anchura,self.altura-18)

        self.rect[1]=pygame.Rect(self.x_disparo-16/2,self.y-self.altura/2+31,16,10)

    def moverse(self,izquierda,derecha):
        movimiento=7.5
        if izquierda==True:
            self.x-=movimiento
            self.x_disparo-=movimiento
        elif derecha==True:
            self.x+=movimiento
            self.x_disparo+=movimiento

    def disparar(self):
        tocar_sonido("jugador_disparo")
        #print("#disparo")
        bala_nueva = Bala(True,self,True)
        bala_jugador.append(bala_nueva)
        self.tecla_levantada=False

    def perder_vida(self, a_perder):
        global pausa, tiempo_pausa,enemigos1
        self.frame_actual=1

        if self.vidas-a_perder>0:
            self.vidas-=a_perder
        else: self.vidas=0

        for i in range(len(balas_enemigo)):
            balas_enemigo[i].viva=False
        if len(bala_jugador)!=0:
            bala_jugador[0].viva=False

        for i in range(len(enemigos1.aliens)):
            enemigos1.aliens[i].frame_actual=2
        jugador0.tecla_levantada=True
        print("HIT")

        pausa=True
        if self.vidas==0:
            self.morir()
        else:
            tiempo_pausa = time.time()


    def morir(self):
        global pausa,mostrar_game_over,ufo0
        self.vidas=0
        self.frame_actual=1
        self.vivo=False
        pausa = True
        mostrar_game_over=True
        ufo0.detener_sonido()



tiempo_pausa = -1

class Bala():
    def __init__(self, direccionArriba,tirador, esJugador):

        if esJugador:
            self.ancho_bala=3
            self.alto_bala=15
        else:
            self.ancho_bala=3 * escalado_sprite
            self.alto_bala=8 * escalado_sprite


        self.viva = True
        self.color=BLANCO
        self.tirador=tirador

        self.frame_actual = 0

        if esJugador:
            self.velocidad=20
        else:
            self.velocidad=10
        #print(tirador)
        self.esJugador = esJugador
        self.x=tirador.x_disparo-self.ancho_bala/2
        self.y=tirador.y_disparo-self.alto_bala
        self.direccionArriba=direccionArriba

        self.tipo = "disparo"

        self.rect = pygame.Rect(self.x,self.y,self.ancho_bala,self.alto_bala)


    def moverse(self,enemigo):
        for k in range(len(enemigo)):
            if enemigo[k].tipo=="grupo_enemigos":
                alienss = enemigo[k].aliens
                for i in range(len(alienss)):
                    rect=alienss[i].rect
                    if self.rect.colliderect(rect) and self.viva is True and alienss[i].vida is True:
                        #print(f"[COLISION] Bala(tirador:{self.tirador.tipo}) con alien(tipo:{alienss[i].tipo})")
                        if self.tirador.tipo=="jugador":
                            bala_jugador.clear()
                            tocar_sonido("matar_enemigo")
                            self.tirador.puntos+=puntos[alienss[i].tipo]
                        alienss[i].vida=False
                        self.viva=False
            elif enemigo[k].tipo=="jugador":
                _jugador = enemigo[k]
                rect = _jugador.rect
                for i in range(len(rect)):
                    if self.rect.colliderect(rect[i]) and self.viva is True:
                        #print(f"[COLISION] Bala(tirador:{self.tirador.tipo}) con jugador")
                        tocar_sonido("jugador_disparado")
                        _jugador.perder_vida(1)
                        self.viva=False
                ##revisar
                for i in range(len(bala_jugador)):
                    if bala_jugador[i].rect.colliderect(self.rect) is True and self.viva:
                        bala_jugador[i].viva=False
                        self.viva=False

            elif enemigo[k].tipo=="obstaculo":
                obstaculos = enemigo[k].obstaculos
                for i in range(len(obstaculos)):
                    rect=obstaculos[i].rect
                    for j in range(len(rect)):
                        if self.rect.colliderect(rect[j]) and self.viva is True and obstaculos[i].vida>0:
                            #print(f"[COLISION] Bala(tirador:{self.tirador.tipo}) con obstaculo")
                            obstaculos[i].vida-=1
                            self.viva=False
                            if self.tirador.tipo=="jugador":
                                bala_jugador.clear()
            elif enemigo[k].tipo=="UFO":
                rect=enemigo[k].rect
                if self.rect.colliderect(rect) and self.viva is True and enemigo[k].vida is True:
                    #print(f"[COLISION] Bala(tirador:{self.tirador.tipo}) con UFO")
                    enemigo[k].vida=False
                    self.tirador.puntos+=puntos['UFO'][random.randint(0,len(puntos['UFO'])-1)]
                    if self.tirador.tipo=="jugador":
                        bala_jugador.clear()
                        tocar_sonido("matar_enemigo")
                    enemigo[k].detener_sonido()



        if self.direccionArriba==True:
            self.y-=self.velocidad
        else: self.y+=self.velocidad
        self.rect = pygame.Rect(self.x,self.y,self.ancho_bala,self.alto_bala)

    def mostrar(self):
        if self.viva is True:
            if self.esJugador:
                pygame.draw.rect(window,self.color,self.rect)

            else:
                if self.frame_actual==0:
                    self.frame_actual=1
                else:
                    self.frame_actual=0
                dimensiones_jugador = sprites['disparo'][0]
                frame_jugador = sprites['disparo'][1][self.frame_actual]
                sprite = mis_sprites.conseguir_sprite(frame_jugador[0],frame_jugador[1],dimensiones_jugador[0],dimensiones_jugador[1], True, self.tipo)
                window.blit(sprite,(self.x,self.y))


def mostrarDatos():
    reloj.tick()
    fps=int(reloj.get_fps())
    #pygame.draw.rect(window,(255,0,0),pygame.Rect(0,alto-15,500,15))
    window.blit(pygame.font.SysFont("Courier new",15).render("{}".format(fps),False,(255,255,255)),(0,PANTALLA_ALTO-17))

    window.blit(pygame.font.SysFont("Courier new",15).render("Enemigos:{}".format(enemigosConVida()),False,(255,255,255)),(30,PANTALLA_ALTO-17))
    window.blit(pygame.font.SysFont("Courier new",15).render("Balas_jugador:{}".format(len(bala_jugador)),False,(255,255,255)),(150,PANTALLA_ALTO-17))
    window.blit(pygame.font.SysFont("Courier new",15).render("Balas_enemigo:{}".format(len(balas_enemigo)),False,(255,255,255)),(300,PANTALLA_ALTO-17))
    window.blit(pygame.font.SysFont("Courier new",15).render("Vidas:{}".format(jugador0.vidas),False,(255,255,255)),(450,PANTALLA_ALTO-17))
    window.blit(pygame.font.SysFont("Courier new",15).render("UFO0_spawn:{}".format(int(ufo0.siguiente_spawn-time.time())),False,(255,255,255)),(550,PANTALLA_ALTO-17))
def enemigosConVida():
    total=0
    for i in range(len(GLOBAL_enemigos)):
        if GLOBAL_enemigos[i].tipo == "grupo_enemigos":
            for j in range(len(GLOBAL_enemigos[i].aliens)):
                if GLOBAL_enemigos[i].aliens[j].vida is True:
                    total+=1
    return total

class Obstaculos():
    def __init__(self):
        self.tipo="obstaculo"
        self.obstaculos=[]
        dim = (21,16)
        self.obstaculos.append(self.Obstaculo((100,725),dim,25))
        self.obstaculos.append(self.Obstaculo((275,725),dim,25))
        self.obstaculos.append(self.Obstaculo((450,725),dim,25))
        self.obstaculos.append(self.Obstaculo((625,725),dim,25))
    def dibujar(self):
        for i in range(len(self.obstaculos)):
            self.obstaculos[i].dibujar()


    class Obstaculo():
        def __init__(self,coordenadas,dimensiones,vidaBase):
            self.x=coordenadas[0]
            self.y=coordenadas[1]
            self.anchura=dimensiones[0] * escalado_sprite
            self.altura=dimensiones[1] * escalado_sprite
            self.vida=vidaBase
            self.rect = [pygame.Rect(self.x,self.y,self.anchura,54),pygame.Rect(self.x,self.y+50,16,22),pygame.Rect(self.x+self.anchura-16,self.y+50,16,22)]
            self.rect_def = pygame.Rect(self.x,self.y,self.anchura,self.altura)


        def dibujar(self):
            if self.vida>0:
                sprite = mis_sprites.conseguir_sprite(sprites['obstaculo'][1][0][0],sprites['obstaculo'][1][0][1],sprites['obstaculo'][0][0],sprites['obstaculo'][0][1], True, "obstaculo")
                window.blit(sprite,self.rect_def)

                pygame.draw.rect(window,NEGRO,pygame.Rect(self.rect_def[0]+13,self.rect_def[1]+25,70,16))


                final = 60 * (self.vida/25)
                porcentaje = pygame.draw.rect(window,(0,255,0),pygame.Rect(self.rect_def[0]+18,self.rect_def[1]+27,final,12))

class UFO():
    def __init__(self):
        global VOLUMEN
        self.tipo="UFO"
        self.vida=False
        self.anchura=sprites[self.tipo][0][0]*escalado_sprite
        self.altura =sprites[self.tipo][0][1]*escalado_sprite
        self.frame = sprites[self.tipo][1]
        self.x=-self.anchura
        self.y=80+50

        self.siguiente_spawn = None

        self.ultimo_moverse = 0


        self.rangos = {'min':7,'max':22}
        self.siguiente_spawn = -1

        self.rect=pygame.Rect(0,0,self.anchura,self.altura)

        self.mixer = pygame.mixer.Sound("assets/sonidos/ufo_10s.wav")
        self.mixer.set_volume(.1)



    def moverse(self):
        global intervalos
        if self.vida:
            if time.time() - self.ultimo_moverse > intervalos['moverseUFO']:
                self.ultimo_moverse = time.time()
                if not(self.x+15>PANTALLA_ANCHO):
                    self.x+=15
                else: self.des_spawn()


    def spawn(self):
        self.x=-self.anchura
        self.sonar()
        self.vida = True

        self.calcular_spawn()

    def des_spawn(self):
        self.vida = False
        self.detener_sonido()
        self.x=-self.anchura

    def calcular_spawn(self):
        m =  random.randint(self.rangos['min'],self.rangos['max'])
        self.siguiente_spawn = time.time() + m
        #print(f"SIGUIENTE UFO EN {m} SEGUNDOS")


    def sonar(self):
        self.mixer.play()

    def detener_sonido(self):
        self.mixer.stop()

    def mostrar(self):
        if self.vida is True:
            self.rect=pygame.Rect(self.x,self.y,self.anchura*0.5,self.altura*0.5)
            #pygame.draw.rect(window,(0,255,0),self.rect)

            sprite=mis_sprites.conseguir_sprite(self.frame[0][0],self.frame[0][1],self.anchura/escalado_sprite,self.altura/escalado_sprite,False,None,.5)
            window.blit(sprite,(self.x,self.y))

obstaculos0=Obstaculos()



enemigos1=grupo_enemigos(MATRIZ,False,5)

jugador0=Jugador()


bala_jugador = []
balas_enemigo = []


bala_explosiones = {'arriba':[],'abajo':[]}


disparando=False

reloj = pygame.time.Clock()
inicio_script = time.time()
intervalo=1          #segundos

ultima_vez = {'moverse':0,'moverseUFO':0, 'sonido0':0}
intervalos = {'moverse':0.2,'moverseUFO':.0415, 'sonido0':0.8}
ufo0=UFO()
GLOBAL_enemigos = [enemigos1,obstaculos0,ufo0]

pausa=False

enemigo_primera_bala=False

aliados=[jugador0,obstaculos0]

#sonido cada 0.8s
min_ufo=5
max_ufo=10


mostrar_game_over = False


estado_juego = 0

inicializado = False

mouse_click = False


hover_jugar = False
hover_salir = False

tiempo_explosion = .05


def reiniciar_valores(reiniciar_puntuacion):
    global jugador0,pausa,mostrar_game_over,tiempo_pausa,enemigos1,GLOBAL_enemigos,obstaculos0,aliados,MATRIZ
    mostrar_game_over=False
    jugador0.vivo = True
    if reiniciar_puntuacion:
        jugador0.puntos=0
        jugador0.vidas=3
    jugador0.frame_actual=0
    jugador0.posicion_central()
    pausa=False
    tiempo_pausa=-1
    enemigos1=grupo_enemigos(MATRIZ,False,5)
    obstaculos0 = None
    obstaculos0=Obstaculos()
    bala_explosiones['arriba'].clear()
    bala_explosiones['abajo'].clear()

    GLOBAL_enemigos = [enemigos1,obstaculos0,ufo0]
    aliados=[jugador0,obstaculos0]
    ufo0.calcular_spawn()
    jugador0.tecla_levantada=True
    print("\n#### GAME RELOADED")

reinicio_pendiente=False

C=0
ufo_tamano_min = 1.2
ufo_tamano_max = 1.4
subiendo=True
__frame=0


cc=False

print(f"\n#### LOADED LANGUAGES: {idiomas}")
print(f"\n#### WINDOW DIMENSIONS: {PANTALLA_ANCHO}x{PANTALLA_ALTO}")
print("\n#### GAME LOADED\n\n\n")
active = True
while active:
    for event in pygame.event.get():
        mouse_click = False

        if event.type == pygame.QUIT:
            active = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_click = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                jugador0.tecla_levantada=True

        if event.type == pygame.KEYDOWN:
            if pausa and mostrar_game_over:
                if event.key == pygame.K_3:
                    tocar_sonido("boton")
                    reiniciar_valores(True)
                if event.key == pygame.K_4:
                    tocar_sonido("boton")
                    reiniciar_valores(True)
                    estado_juego = 0
                    inicializado=False





    if estado_juego == 0:       ## MENU PRINCIPAL
        limpiar()
        pygame.mouse.set_visible(True)
        ## TITULO

        ##### MENU ALIENS
        ## ANIM ALIEN MENU
        if (C==0 and not subiendo) or (C==100 and subiendo):
            subiendo=not subiendo

        if subiendo: C+=5
        else: C-=5

        tamano = round((C/100 * ufo_tamano_min) + ((1-C/100) * ufo_tamano_max),2)
        __frame = int(int(time.time())%2==0)


        image = pygame.image.load('assets/sprites/logo.png')
        window.blit(image, image.get_rect(center=(PANTALLA_ANCHO/2,300/2)))


        resta = 150

        ## TITLE & SUBTITLE
        subtitulo = pygame.font.Font(("assets/fuente.ttf"),25).render(trad("autor",idioma),False,(255,255,255))
        window.blit(subtitulo,subtitulo.get_rect(center=(PANTALLA_ANCHO/2,290)))

        ## PLAY BUTTON
        boton_jugar=pygame.draw.rect(window,(BLANCO if hover_jugar is False else (255,226,0)),(PANTALLA_ANCHO/2 - 375/2,350,375,70),width=(3 if hover_jugar is False else 0))
        texto = pygame.font.Font(("assets/fuente.ttf"),35).render(trad("boton_jugar",idioma),False,BLANCO if hover_jugar is False else NEGRO)
        window.blit(texto, texto.get_rect(center=(PANTALLA_ANCHO/2, 350+70/2+5)))

        ## EXIT BUTTON
        boton_salir=pygame.draw.rect(window,(BLANCO if hover_salir is False else (255,226,0)),(PANTALLA_ANCHO/2 - 375/2,450,375,70),width=(3 if hover_salir is False else 0))
        texto = pygame.font.Font(("assets/fuente.ttf"),35).render(trad("boton_salir",idioma),False,BLANCO if hover_salir is False else NEGRO)
        window.blit(texto, texto.get_rect(center=(PANTALLA_ANCHO/2, 450+70/2+5)))

        ## LANGUAGE BUTTON
        boton_idioma = pygame.draw.rect(window,(0,0,0),pygame.Rect(PANTALLA_ANCHO/2 - 25*escalado_sprite//2 -resta ,600,25*escalado_sprite,25*escalado_sprite))
        bandera='bandera_'+idiomas[idioma]
        _sprite=mis_sprites.conseguir_sprite(sprites["bandera"][1][idioma][0],sprites["bandera"][1][idioma][1],sprites["bandera"][0][0],sprites["bandera"][0][1],False,None)
        window.blit(_sprite,(PANTALLA_ANCHO/2 - 25*escalado_sprite//2 -resta ,600))

        ## VOLUME BUTTON
        boton_volumen = pygame.draw.rect(window,(0,0,0),pygame.Rect(PANTALLA_ANCHO/2 - 15*escalado_sprite//2 -resta,750,15*escalado_sprite,15*escalado_sprite))
        imagen = int (not VOLUMEN)
        _sprite=mis_sprites.conseguir_sprite(sprites['volumen'][1][imagen][0],sprites['volumen'][1][imagen][1],sprites['volumen'][0][0],sprites['volumen'][0][1],False,None,0.9)
        window.blit(_sprite,(PANTALLA_ANCHO/2 - 13*(escalado_sprite*0.9)//2 -resta ,750 + 7 * (escalado_sprite//2)-3 ))


        test=450
        test_2=-50

        ## TABLE OF ALIEN POINTS
        _sprite=mis_sprites.conseguir_sprite(sprites['P'][1][__frame][0],sprites['P'][1][__frame][1],sprites['P'][0][0],sprites['P'][0][1],True,"P",1.5)
        window.blit(_sprite,(PANTALLA_ANCHO - test,530-test_2))

        texto = pygame.font.Font(("assets/fuente.ttf"),21).render(" + 10 "+trad("puntos",idioma),False,BLANCO)
        window.blit(texto, (PANTALLA_ANCHO - test +80, 550-test_2))


        _sprite=mis_sprites.conseguir_sprite(sprites['C1'][1][__frame][0],sprites['C1'][1][__frame][1],sprites['C1'][0][0],sprites['C1'][0][1],True,"C1",1.5)
        window.blit(_sprite,(PANTALLA_ANCHO - test ,530+70*1-test_2))

        texto = pygame.font.Font(("assets/fuente.ttf"),21).render(" + 20 "+trad("puntos",idioma),False,BLANCO)
        window.blit(texto, (PANTALLA_ANCHO - test+80, 550+70*1-test_2))


        _sprite=mis_sprites.conseguir_sprite(sprites['C0'][1][__frame][0],sprites['C0'][1][__frame][1],sprites['C0'][0][0],sprites['C0'][0][1],True,"C0",1.5)
        window.blit(_sprite,(PANTALLA_ANCHO - test +10,530+70*2-test_2))

        texto = pygame.font.Font(("assets/fuente.ttf"),21).render(" + 30 "+trad("puntos",idioma),False,BLANCO)
        window.blit(texto, (PANTALLA_ANCHO - test+80, 550+70*2-test_2))


        _sprite=mis_sprites.conseguir_sprite(sprites['UFO'][1][0][0],sprites['UFO'][1][0][1],sprites['UFO'][0][0],sprites['UFO'][0][1],True,"UFO",.55)
        window.blit(_sprite,(PANTALLA_ANCHO - test ,530+70*3-test_2))

        texto = pygame.font.Font(("assets/fuente.ttf"),21).render(" + ??? "+trad("puntos",idioma),False,BLANCO)
        window.blit(texto, (PANTALLA_ANCHO - test+80, 550+70*3 -15-test_2))

        bord_H = 10
        bord_V = 20

        pygame.draw.rect(window,(255,255,255),pygame.Rect(PANTALLA_ANCHO - test -bord_H,530-bord_V-test_2,247+bord_H*2,245+bord_V*2), width=2)




        ## MOUSE HOVER-CLICK CHECKS
        pos_mouse = pygame.mouse.get_pos()


        if boton_jugar.collidepoint(pos_mouse):
            hover_jugar = True
            if mouse_click:
                tocar_sonido("boton")
                estado_juego=1
                limpiar()
        else:
            hover_jugar = False

        if boton_salir.collidepoint(pos_mouse):
            hover_salir = True
            if mouse_click:
                tocar_sonido("boton")
                active=False
        else:
            hover_salir = False

        if boton_idioma.collidepoint(pos_mouse):
            color_borde_0 = (150,150,150)
            if mouse_click:
                tocar_sonido("boton")
                if idioma!=len(idiomas)-1:
                    idioma+=1
                else:
                    idioma=0
                mouse_click=False
        else:
            color_borde_0 = (255,255,255)

        if boton_volumen.collidepoint(pos_mouse):
            color_borde_1 = (150,150,150)
            if mouse_click:
                VOLUMEN = int(not VOLUMEN)
                tocar_sonido("boton")
                mouse_click=False
        else:
            color_borde_1 = (255,255,255)


        ## LANGUAGE & VOLUME BUTTON BORDERS
        pygame.draw.rect(window,color_borde_0,pygame.Rect(PANTALLA_ANCHO/2 - 25*escalado_sprite//2-4-resta,600-4,25*escalado_sprite+8,25*escalado_sprite+8), width=2)
        pygame.draw.rect(window,color_borde_1,pygame.Rect(PANTALLA_ANCHO/2 - 15*escalado_sprite//2-4-resta,750-4,15*escalado_sprite+8,15*escalado_sprite+8), width=2)


        pygame.time.Clock().tick(60)
        pygame.display.update()

    elif estado_juego == 1:
        ## GAME
        limpiar()
        pygame.mouse.set_visible(False)

        for expl in bala_explosiones['abajo']:
            if (time.time()-expl['iniciado'])>tiempo_explosion:
                bala_explosiones['abajo'].remove(expl)
        for expl in bala_explosiones['arriba']:
            if (time.time()-expl['iniciado'])>tiempo_explosion:
                bala_explosiones['arriba'].remove(expl)


        if tiempo_pausa!=-1:
            if pausa is True:
                if time.time()-tiempo_pausa>3:
                    tiempo_pausa=-1
                    pausa=False
                    jugador0.frame_actual=0
                    jugador0.posicion_central()

                    ufo0.des_spawn()
                    ufo0.calcular_spawn()


                    if reinicio_pendiente:
                        enemigos1=grupo_enemigos(MATRIZ,False,5)
                        obstaculos0=Obstaculos()
                        bala_explosiones['arriba'].clear()
                        bala_explosiones['abajo'].clear()
                        GLOBAL_enemigos = [enemigos1,obstaculos0,ufo0]



        if not inicializado:
            print(f"\nGAME STARTED | Alien QTY:{enemigosConVida()}")
            enemigos1.mostrar()
            jugador0.dibujar()
            inicializado=True
            ufo0.des_spawn()
            ufo0.calcular_spawn()

        ahora = time.time()


        for bala in bala_jugador:
            if not BORDES_PANTALLA[0] <= bala.rect.centery <= BORDES_PANTALLA[1] and bala.viva:
                bala.ancho_bala = 17 * escalado_sprite
                bala.alto_bala = 15 * escalado_sprite
                bala_explosiones['arriba'].append({'iniciado':time.time(),'coordenadas':[bala.x-bala.ancho_bala//4,bala.y]})
                bala_jugador.remove(bala)


        for bala in balas_enemigo:
            if not BORDES_PANTALLA[0] <= bala.rect.centery <= BORDES_PANTALLA[1] and bala.viva:
                bala.ancho_bala = 8 * escalado_sprite
                bala.alto_bala = 8 * escalado_sprite
                bala_explosiones['abajo'].append({'iniciado':time.time(),'coordenadas':[bala.x-bala.ancho_bala//2,PANTALLA_ALTO-60]})
                balas_enemigo.remove(bala)

        bala_jugador = [bala for bala in bala_jugador if BORDES_PANTALLA[0] <= bala.rect.centery <= BORDES_PANTALLA[1]]
        balas_enemigo = [bala for bala in balas_enemigo if BORDES_PANTALLA[0] <= bala.rect.centery <= BORDES_PANTALLA[1]]

        if enemigosConVida()==0 and not reinicio_pendiente:
            reiniciar_valores(False)
            print("0 aliens alive")

        if pausa is False:
            if enemigo_primera_bala is False:
                if ahora-inicio_script>0.5:
                    enemigo_primera_bala=True
                    enemigos1.disparar()
            else: enemigos1.disparar()


            if ufo0.vida is False and ahora-ufo0.siguiente_spawn>0:
                ufo0.spawn()


            if ahora-ultima_vez['moverse']> intervalos['moverse']:
                ultima_vez['moverse']=ahora
                enemigos1.mover()

            ufo0.moverse()


            teclas = pygame.key.get_pressed()
            if jugador0.x>5 and (teclas[pygame.K_LEFT] or teclas[pygame.K_a]):
                jugador0.moverse(True,False)
            if jugador0.x<PANTALLA_ANCHO-(jugador0.anchura+5) and (teclas[pygame.K_RIGHT] or teclas[pygame.K_d]):
                jugador0.moverse(False,True)
            if teclas[pygame.K_SPACE]:
                if len(bala_jugador)==0 and jugador0.tecla_levantada:
                    jugador0.disparar()

            for bala in range(len(bala_jugador)):
                bala_jugador[bala].moverse(GLOBAL_enemigos)
                if len(bala_jugador)>0:
                    bala_jugador[bala].mostrar()
            for bala in range(len(balas_enemigo)):
                balas_enemigo[bala].moverse(aliados)
                if len(balas_enemigo)>0:
                    balas_enemigo[bala].mostrar()



        window.blit(pygame.font.Font(("assets/fuente.ttf"),20).render(trad("puntuacion",idioma)+"< 1 >",False,(255,255,255)),(10,15))
        pts = visual_puntos(jugador0.puntos)
        window.blit(pygame.font.Font(("assets/fuente.ttf"),25).render("{}".format(pts),False,(255,255,255)),(60,40))

        window.blit(pygame.font.Font(("assets/fuente.ttf"),20).render("{}".format(jugador0.vidas),False,(255,255,255)),(680,15))
        if jugador0.vidas>1:
            window.blit(pygame.font.Font(("assets/fuente.ttf"),20).render(trad("vidas",idioma),False,(255,255,255)),(700,15))
        else: window.blit(pygame.font.Font(("assets/fuente.ttf"),20).render(trad("vida",idioma),False,(255,255,255)),(700,15))
        #sprite=mis_sprites.conseguir_sprite(ssprite[1][0][0],ssprite[1][0][1],ssprite[0][0],ssprite[0][1],False,None)

        dimensiones_jugador = sprites['jugador'][0]
        frame_jugador = sprites['jugador'][1][0]
        _sprite = mis_sprites.conseguir_sprite(frame_jugador[0],frame_jugador[1],dimensiones_jugador[0],dimensiones_jugador[1], True, "jugador")
        for i in range(0,jugador0.vidas-1):
            window.blit(_sprite,(595-i*80,10))




        ufo0.mostrar()
        enemigos1.mostrar()
        jugador0.dibujar()
        obstaculos0.dibujar()


        if mostrar_game_over:
            pygame.draw.rect(window,NEGRO,pygame.Rect(PANTALLA_ANCHO//2 - 600/2, PANTALLA_ALTO//2-200, 600, 300))

            texto = pygame.font.Font(("assets/fuente.ttf"),35).render(trad("texto_gover",idioma),False,ROJO)
            text_rect = texto.get_rect(center=(PANTALLA_ANCHO/2, PANTALLA_ALTO/2-160))
            window.blit(texto, text_rect)

            texto = pygame.font.Font(("assets/fuente.ttf"),27).render(trad("puntuacion",idioma) + f": {visual_puntos(jugador0.puntos)}",False,ROJO)
            text_rect = texto.get_rect(center=(PANTALLA_ANCHO/2, PANTALLA_ALTO/2-100))
            window.blit(texto, text_rect)

            texto = pygame.font.Font(("assets/fuente.ttf"),23).render(trad("texto_reintentar",idioma),False,ROJO)
            text_rect = texto.get_rect(center=(PANTALLA_ANCHO/2, PANTALLA_ALTO/2+20))
            window.blit(texto, text_rect)

            texto = pygame.font.Font(("assets/fuente.ttf"),23).render(trad("texto_salir",idioma),False,ROJO)
            text_rect = texto.get_rect(center=(PANTALLA_ANCHO/2, PANTALLA_ALTO/2+50))
            window.blit(texto, text_rect)

        #explosiones = [{'iniciado':-1, 'coordenadas':[50,50]}]

        for i in range(len(bala_explosiones['arriba'])):
            dimensiones = sprites['disparo_explosion'][0]
            frame = sprites['disparo_explosion'][1][0]
            sprite = mis_sprites.conseguir_sprite(frame[0],frame[1],dimensiones[0],dimensiones[1], True, "disparo_explosion")
            window.blit(sprite,(bala_explosiones['arriba'][i]['coordenadas'][0],bala_explosiones['arriba'][i]['coordenadas'][1]))



        for i in range(len(bala_explosiones['abajo'])):
            dimensiones = sprites['disparo_explosion'][0]
            frame = sprites['disparo_explosion'][1][1]
            sprite = mis_sprites.conseguir_sprite(frame[0],frame[1],dimensiones[0],dimensiones[1], True, "disparo_explosion")
            window.blit(sprite,(bala_explosiones['abajo'][i]['coordenadas'][0],bala_explosiones['abajo'][i]['coordenadas'][1]))


        pygame.draw.rect(window,ROJO,pygame.Rect(0,BORDES_PANTALLA[1]+25,PANTALLA_ANCHO,2))


        if enemigos1.mas_baja>=BORDES_PANTALLA[1]:
            jugador0.perder_vida(3)
        if DEBUG: mostrarDatos()

        pygame.time.Clock().tick(60)
        pygame.display.update()