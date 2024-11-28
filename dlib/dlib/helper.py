from IPython.display import Markdown, display
def printmd(*args):
    display(Markdown(' '.join(args)))


import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from typing import List, Tuple, Union


class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other: 'Vector') -> 'Vector':
        return Vector(self.x + other.x, self.y + other.y)

    def __repr__(self):
        return f"Vector(x={self.x}, y={self.y})"


class AnimatedVector:
    def __init__(self, start_positions: List[Vector], deltas: List[Vector], color: str = 'b', name: str = 'vector'):
        if len(start_positions) != len(deltas):
            raise ValueError("start_positions and deltas must have the same length.")
        self.start_positions = start_positions
        self.deltas = deltas
        self.color = color
        self.name = name

class StaticVector:
    def __init__(self, start_position: Vector, delta: Vector, color: str = 'w', name: str = 'static_vector'):
        self.start_position = start_position
        self.delta = delta
        self.color = color
        self.name = name


class SceneMaker:

    def setup(self, animated_vectors: List[AnimatedVector], static_vectors: List[StaticVector]) -> None:
        pass

    def animate(self, name: str) -> None:
        pass

    def display(self):
        pass

class MatplotlibScene(SceneMaker):

    def setup(self, animated_vectors: List[AnimatedVector], static_vectors: List[StaticVector]) -> None:
        self.animated_vectors = animated_vectors
        self.static_vectors = static_vectors
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect('equal')
        largest = 0

        # Determine plot limits dynamically
        for vector in self.animated_vectors:
            for start, delta in zip(vector.start_positions, vector.deltas):
                end = start + delta
                largest = max(
                    largest,
                    abs(end.x), abs(end.y),
                    abs(start.x), abs(start.y)
                )
        
        for vector in self.static_vectors:
            end = vector.start_position + vector.delta
            largest = max(
                largest,
                abs(end.x), abs(end.y),
                abs(vector.start_position.x), abs(vector.start_position.y)
            )

        self.ax.set_xlim([-1.2 * largest, 1.2 * largest])
        self.ax.set_ylim([-1.2 * largest, 1.2 * largest])
        self.ax.grid()

        quivers = []  # To store quiver objects for updating in animation

        # Initialize static vectors
        for vector in self.static_vectors:
            self.ax.quiver(
                vector.start_position.x, vector.start_position.y,
                vector.delta.x, vector.delta.y,
                angles='xy', scale_units='xy', scale=1,
                color=vector.color, label=vector.name
            )

        # Initialize animated vectors
        for vector in self.animated_vectors:
            quiver = self.ax.quiver(
                [vec.x for vec in vector.start_positions],
                [vec.y for vec in vector.start_positions],
                [vec.x for vec in vector.deltas],
                [vec.y for vec in vector.deltas],
                angles='xy', scale_units='xy', scale=1,
                color=vector.color, label=vector.name
            )
            quivers.append(quiver)

        self.ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

        def update(frame):
            for quiver, vector in zip(quivers, self.animated_vectors):
                start = vector.start_positions[frame]
                delta = vector.deltas[frame]
                quiver.set_offsets([[start.x, start.y]])  # Update start position
                quiver.set_UVC(delta.x, delta.y)  # Update vector direction and magnitude
            return quivers

        self.update_fn = update

    def display(self):
        plt.show()

    def animate(self, name: str):

        # Create animation
        frames = len(self.animated_vectors[0].start_positions)  # Assume all vectors have the same number of frames
        anim = FuncAnimation(self.fig, self.update_fn, frames=frames, interval=100, blit=True)
        anim.save(f'video/{name}.gif', writer='imagemagick', fps=5)


class VectorScene():
    def __init__(self, scene_maker: SceneMaker= None):
        self.setup_called = False
        self.animated_vectors: List[AnimatedVector] = []  # Store AnimatedVector objects
        self.static_vectors: List[StaticVector] = []  # Store StaticVector objects
        self.scene_maker = scene_maker
        if scene_maker is None:
            self.scene_maker = MatplotlibScene()

    @staticmethod
    def _convert_to_vectors(vector_list: List[Union[List[float], Tuple[float, float]]]) -> List[Vector]:
        return [Vector(v[0], v[1]) for v in vector_list]

    def add_animated_vector(self, deltas: List[Union[List[float], Tuple[float, float]]], color: str = 'b', name: str = 'vector') -> 'AnimatedVectorScene':
        start_positions = [[0, 0] for _ in deltas]
        return self.add_animated_vector_at(start_positions, deltas, color, name)

    def add_animated_vector_at(self, start_positions: List[Union[List[float], Tuple[float, float]]], deltas: List[Union[List[float], Tuple[float, float]]], color: str = 'b', name: str = 'vector') -> 'AnimatedVectorScene':
        start_positions = self._convert_to_vectors(start_positions)
        deltas = self._convert_to_vectors(deltas)
        self.animated_vectors.append(AnimatedVector(start_positions, deltas, color, name))
        return self

    def add_vector(self, delta: Union[List[float], Tuple[float, float]], color: str = 'w', name: str = 'static_vector') -> 'AnimatedVectorScene':
        return self.add_vector_at([0, 0], delta, color, name)
    
    def add_vector_at(self, start_position: Union[List[float], Tuple[float, float]], delta: Union[List[float], Tuple[float, float]], color: str = 'w', name: str = 'static_vector') -> 'AnimatedVectorScene':
        start_position = Vector(*start_position)
        delta = Vector(*delta)
        self.static_vectors.append(StaticVector(start_position, delta, color, name))
        return self
    
    def setup(self):
        if self.setup_called:
            return
        self.setup_called = True

        self.scene_maker.setup(self.animated_vectors, self.static_vectors)

    def animate(self, name: str):
        self.setup()
        self.scene_maker.animate(name)

    def display(self):
        self.setup()
        self.scene_maker.display()
    
