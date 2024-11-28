from IPython.display import Markdown, display
def printmd(*args):
    display(Markdown(' '.join(args)))

import matplotlib.pyplot as plt


class VectorScene():
    def __init__(self):
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots()
        self.vectors = []
    
    def add_vector(self, vector, color='b', label='vector'):
        # if we have a tf vector, convert it to numpy
        if hasattr(vector, 'numpy'):
            vector = vector.numpy()
        self.add_vector_at([0,0], vector, color, label)
        return self

    def add_vector_at(self, start_vector, delta_vector, color='b', name='vector'):
        # if we have a tf vector, convert it to numpy
        if hasattr(start_vector, 'numpy'):
            start_vector = start_vector.numpy()
        if hasattr(delta_vector, 'numpy'):
            delta_vector = delta_vector.numpy()
        self.vectors.append((start_vector, delta_vector, color, name))
        return self
        

    def display(self):
        self.ax.set_aspect('equal')
        for start_vector, delta_vector, color, label in self.vectors:
            self.ax.quiver(start_vector[0], start_vector[1], delta_vector[0], delta_vector[1], angles='xy', scale_units='xy', scale=1, color=color, label=label)
        x_max = max([v[0][0]+v[1][0] for v in self.vectors])
        y_max = max([v[0][1]+v[1][1] for v in self.vectors])
        x_min = min([v[0][0] for v in self.vectors])
        y_min = min([v[0][1] for v in self.vectors])
        largest = max(x_max, x_min, y_max, y_min)
        
        self.ax.set_xlim([-1.2*largest, 1.2*largest])
        self.ax.set_ylim([-1.2*largest, 1.2*largest])
        # add a x and y axis
        plt.grid()
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.show()


from matplotlib.animation import FuncAnimation

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


class AnimatedVectorScene:
    def __init__(self):
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots()
        self.animated_vectors: List[AnimatedVector] = []  # Store AnimatedVector objects

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

    def _set_scene(self):
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

        self.ax.set_xlim([-1.2 * largest, 1.2 * largest])
        self.ax.set_ylim([-1.2 * largest, 1.2 * largest])
        self.ax.grid()

        quivers = []  # To store quiver objects for updating in animation

        # Initialize quivers
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

        return update

    def display(self):
        update = self._set_scene()
        plt.show()

    def animate(self, name: str, interval: int = 100):
        # Create animation
        frames = len(self.animated_vectors[0].start_positions)  # Assume all vectors have the same number of frames
        anim = FuncAnimation(self.fig, self._set_scene(), frames=frames, interval=interval, blit=True)
        anim.save(f'video/{name}.gif', writer='imagemagick', fps=5)
