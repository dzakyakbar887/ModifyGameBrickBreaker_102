import colorsys
import tkinter as tk


# Game Object Class
class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


# Ball Class
class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 15  # sebelumnya 10
        self.hue = 0.0   # untuk warna pelangi

        # bola berbentuk segitiga (ujung menghadap atas)
        item = canvas.create_polygon(
            x, y - self.radius,                  # puncak
            x - self.radius, y + self.radius,    # kiri bawah
            x + self.radius, y + self.radius,    # kanan bawah
            fill='white'
        )

        super(Ball, self).__init__(canvas, item)

    def get_position(self):
        # polygon punya 6 koordinat, jadi diubah ke kotak pembatas [x1, y1, x2, y2]
        coords = self.canvas.coords(self.item)
        xs = coords[0::2]
        ys = coords[1::2]
        return [min(xs), min(ys), max(xs), max(ys)]

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()

        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1

        if coords[1] <= 0:
            self.direction[1] *= -1

        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed

        self.move(x, y)
        self.rainbow()

    def rainbow(self):
        # putar warna melewati seluruh spektrum pelangi
        self.hue = (self.hue + 0.02) % 1.0
        r, g, b = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
        color = '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))
        self.canvas.itemconfig(self.item, fill=color)

    def collide(self, game_objects):
        if not game_objects:
            return

        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()
                self.direction[1] *= -1
                # makin lama makin cepat, maksimal 18
                self.speed = min(self.speed + 0.2, 18)

            elif isinstance(game_object, Paddle):
                paddle_coords = game_object.get_position()

                if x < paddle_coords[0] + game_object.width / 3:
                    self.direction[0] = -1
                elif x > paddle_coords[2] - game_object.width / 3:
                    self.direction[0] = 1

                self.direction[1] = -1


# Paddle Class
class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None

        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill='yellow'
        )

        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()

        # batasi supaya paddle menempel di tepi, tidak keluar layar
        if coords[0] + offset < 0:
            offset = -coords[0]
        elif coords[2] + offset > width:
            offset = width - coords[2]

        if offset != 0:
            super(Paddle, self).move(offset, 0)

            if self.ball is not None:
                self.ball.move(offset, 0)


# Brick Class
class Brick(GameObject):
    COLORS = {
        1: '#e74c3c',
        2: '#3498db',
        3: '#222222'
    }

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits

        # posisi horizontal menentukan warna awal, jadi efeknya seperti gelombang pelangi
        self.hue_offset = x / 610.0

        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill=Brick.rainbow_color(self.hue_offset),
            # brick 2x pukulan diberi garis tepi putih tebal sebagai penanda
            outline='white' if hits > 1 else 'black',
            width=3 if hits > 1 else 1,
            tags='brick'
        )

        super(Brick, self).__init__(canvas, item)

    @staticmethod
    def rainbow_color(hue):
        r, g, b = colorsys.hsv_to_rgb(hue % 1.0, 1.0, 1.0)
        return '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))

    def set_hue(self, base_hue):
        self.canvas.itemconfig(
            self.item,
            fill=Brick.rainbow_color(base_hue + self.hue_offset)
        )

    def hit(self):
        self.hits -= 1

        if self.hits <= 0:
            self.delete()
        else:
            # setelah kena sekali, garis tepi kembali normal
            self.canvas.itemconfig(
                self.item,
                outline='black',
                width=1
            )


# Game Class
class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)

        self.lives = 3
        self.width = 610
        self.height = 400

        self.canvas = tk.Canvas(
            self,
            bg='#aaaaff',
            width=self.width,
            height=self.height
        )

        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None

        self.paddle = Paddle(
            self.canvas,
            self.width / 2,
            326
        )

        self.items[self.paddle.item] = self.paddle

        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 2)
            self.add_brick(x + 37.5, 70, 1)
            self.add_brick(x + 37.5, 90, 1)

        self.hud = None
        self.setup_game()

        self.canvas.focus_set()

        # paddle: gerak mulus selama tombol ditahan
        self.paddle_speed = 14   # piksel per tick (~60 tick/detik)
        self.keys = set()

        self.canvas.bind('<KeyPress-Left>', lambda e: self.keys.add('Left'))
        self.canvas.bind('<KeyRelease-Left>', lambda e: self.keys.discard('Left'))
        self.canvas.bind('<KeyPress-Right>', lambda e: self.keys.add('Right'))
        self.canvas.bind('<KeyRelease-Right>', lambda e: self.keys.discard('Right'))

        self.paddle_loop()

        self.brick_hue = 0.0
        self.animate_bricks()

    def animate_bricks(self):
        # geser warna semua brick supaya pelangi bergerak
        self.brick_hue = (self.brick_hue + 0.01) % 1.0

        for obj in self.items.values():
            if isinstance(obj, Brick):
                obj.set_hue(self.brick_hue)

        self.after(50, self.animate_bricks)

    def paddle_loop(self):
        offset = 0

        if 'Left' in self.keys:
            offset -= self.paddle_speed
        if 'Right' in self.keys:
            offset += self.paddle_speed

        if offset != 0:
            self.paddle.move(offset)

        self.after(16, self.paddle_loop)

    def setup_game(self):
        self.add_ball()
        self.update_lives_text()

        self.text = self.draw_text(
            300,
            200,
            'Press Space to start'
        )

        self.canvas.bind(
            '<space>',
            lambda event: self.start_game()
        )

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()

        paddle_coords = self.paddle.get_position()

        x = (paddle_coords[0] + paddle_coords[2]) * 0.5

        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size=40):
        font = ('Forte', size)

        return self.canvas.create_text(
            x,
            y,
            text=text,
            font=font
        )

    def update_lives_text(self):
        text = 'Lives: %s' % self.lives

        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(
                self.hud,
                text=text
            )

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)

        self.paddle.ball = None

        self.game_loop()

    def game_loop(self):
        self.check_collisions()

        num_bricks = len(
            self.canvas.find_withtag('brick')
        )

        if num_bricks == 0:
            self.ball.speed = None
            self.draw_text(300, 200, 'You win!')

        elif self.ball.get_position()[3] >= self.height:
            self.ball.speed = None
            self.lives -= 1
            self.update_lives_text()

            if self.lives <= 0:
                self.draw_text(
                    300,
                    200,
                    'You Lose!!! Game Over!',
                    25
                )
            else:
                self.after(1000, self.setup_game)

        else:
            self.ball.update()
            self.after(20, self.game_loop)  # sebelumnya 50

    def check_collisions(self):
        ball_coords = self.ball.get_position()

        items = self.canvas.find_overlapping(
            *ball_coords
        )

        objects = [
            self.items[x]
            for x in items
            if x in self.items
        ]

        self.ball.collide(objects)


# Main Program
if __name__ == '__main__':
    root = tk.Tk()

    root.title('Hello, Jarvis!')

    game = Game(root)

    game.mainloop()