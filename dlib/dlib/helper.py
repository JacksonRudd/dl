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


class AnimatedVectorScene:
    def __init__(self):
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots()
        self.animated_vectors = []  # Store animated vectors as (start_list, delta_list, color, name)
    
    def add_animated_vector(self, vector_list, color='b', label='vector'):
        self.add_animated_vector_at([[0, 0]] * len(vector_list), vector_list, color, label)
        return self

    def add_animated_vector_at(self, start_vector_list, delta_vector_list, color='b', name='vector'):
        if len(start_vector_list) != len(delta_vector_list):
            raise ValueError("start_vector_list and delta_vector_list must have the same length.")
        
        self.animated_vectors.append((start_vector_list, delta_vector_list, color, name))
        return self

    def _set_scene(self):
        self.ax.set_aspect('equal')
        largest = 0

        # Determine plot limits dynamically
        for starts, deltas, _, _ in self.animated_vectors:
            for start, delta in zip(starts, deltas):
                end_x = start[0] + delta[0]
                end_y = start[1] + delta[1]
                largest = max(largest, abs(end_x), abs(end_y), abs(start[0]), abs(start[1]))

        self.ax.set_xlim([-1.2 * largest, 1.2 * largest])
        self.ax.set_ylim([-1.2 * largest, 1.2 * largest])
        plt.grid()

        quivers = []  # To store quiver objects for updating in animation

        # Initialize quivers
        for start, end, color, label in self.animated_vectors:
            quiver = self.ax.quiver(
                start[0], start[1], end[0], end[1], angles='xy', scale_units='xy', scale=1, color=color, label=label
            )
            quivers.append(quiver)
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        def update(frame):
            for quiver, (starts, deltas, _, _) in zip(quivers, self.animated_vectors):
                start = starts[frame]
                delta = deltas[frame]
                quiver.set_offsets([start])  # Update start position
                quiver.set_UVC(delta[0], delta[1])  # Update vector direction and magnitude
            return quivers
        return update

    def display(self, fig_num=1):
        update = self._set_scene()
        quivers = update(0)

        plt.show()

    def animate(self,name, interval=100):
        # Create animation
        frames = len(self.animated_vectors[0][0])  # Assume all vectors have the same number of frames
        anim = FuncAnimation(self.fig, self._set_scene(), frames=frames, interval=interval, blit=True)
        anim.save(f'video/{name}.gif', writer='imagemagick', fps=5)