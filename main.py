import tkinter
from tkinter import *
from tkinter import ttk
import threading
import time

global initial_x, initial_y, image_cords, move, dfs_time


class Vertex:
    def __init__(self, circle):
        self.circle = circle
        self.name = None
        self.predecessor = None
        self.discovery_time = None
        self.finish_time = None
        self.color = "white"
        self.color_label = None


class Application(ttk.Frame):
    adjacency_matrix = []
    vertices = []

    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.master = master

        # Name and res
        master.title('Graph Algorithm Visualizer')
        master.geometry("800x600")

        # Frame container setups
        self.nav_frame = Frame(master, width=750, height=50, padx=15)
        self.canvas = Canvas(master, width=775, height=450, bg="white")
        self.btm_nav = Frame(master)
        self.btm_nested_nav = Frame(self.btm_nav)

        # Configure grids for Frames
        master.grid_rowconfigure(1, weight=1)
        master.grid_columnconfigure(0, weight=1)

        self.nav_frame.grid(row=0, sticky="ew")
        self.nav_frame.columnconfigure(0, weight=1)
        self.nav_frame.columnconfigure(1, weight=2)

        self.canvas.grid(sticky=NS + EW, row=1, padx=15, pady=(0, 15))
        self.canvas.grid_columnconfigure(0, weight=1)
        self.canvas.grid_rowconfigure(0, weight=1)

        self.btm_nav.grid(row=2, sticky="ew", padx=15)
        self.btm_nav.columnconfigure(0, weight=1)
        self.btm_nav.columnconfigure(1, weight=2)

        self.btm_nested_nav.grid(sticky=W, row=2)
        self.btm_nested_nav.columnconfigure(0, weight=1)
        self.btm_nested_nav.rowconfigure(1, weight=1)

        # Widgets
        # Top Nav
        label_title = ttk.Label(self.nav_frame, text="GraphAlgo", font=("Helvetica", 25))
        dfs_title = ttk.Label(self.nav_frame, text="Depth First Search", font=("Helvetica", 15))

        # Bottom Nav
        self.coords_info = ttk.Label(self.btm_nested_nav, text="x: 0, y: 0", font=("Helvetica", 10))
        spawn_vertex_btn = ttk.Button(self.nav_frame, text="Spawn Vertex", command=self.spawn_vertex)
        clear_canvas_btn = ttk.Button(self.nav_frame, text="Clear Canvas",
                                      command=lambda: self.clear_canvas(spawn_vertex_btn,
                                                                        label_btn, next_btn, connect_btn))
        label_btn = ttk.Button(self.btm_nested_nav, text="Label Vertices",
                               command=lambda: self.label_vertices(spawn_vertex_btn, label_btn, next_btn))
        connect_vertex_label = ttk.Label(self.btm_nested_nav, text="Vertex: ")
        first_vertex_entry = ttk.Entry(self.btm_nested_nav)
        to_vertex_label = ttk.Label(self.btm_nested_nav, text="To")
        second_vertex_entry = ttk.Entry(self.btm_nested_nav)
        connect_btn = ttk.Button(self.btm_nested_nav, text="Connect", command=self.draw_lines)
        next_btn = ttk.Button(self.btm_nav, text="Next", command=lambda: self.start_thread(next_btn,
                                                                                           clear_canvas_btn,
                                                                                           connect_btn))
        next_btn["state"] = "disabled"

        # Variable Watchers
        self.entry_one = tkinter.StringVar()
        self.entry_two = tkinter.StringVar()
        first_vertex_entry["textvariable"] = self.entry_one
        second_vertex_entry["textvariable"] = self.entry_two

        # Grid layout for widgets
        label_title.grid(row=0, column=0, sticky=W)
        dfs_title.grid(row=0, column=1, sticky=E)
        spawn_vertex_btn.grid(row=1, column=0, sticky=W, pady=15)
        clear_canvas_btn.grid(row=1, column=1, sticky=E, pady=15)

        label_btn.grid(column=0, row=0, pady=(0, 15))
        connect_vertex_label.grid(column=1, row=0, pady=(0, 15))
        first_vertex_entry.grid(column=2, row=0, pady=(0, 15))
        to_vertex_label.grid(column=3, row=0, pady=(0, 15))
        second_vertex_entry.grid(column=4, row=0, pady=(0, 15))
        connect_btn.grid(column=5, row=0, padx=2, pady=(0, 15))
        self.coords_info.grid(row=0, column=6, pady=(0, 15))
        next_btn.grid(column=1, row=2, sticky=E, pady=(0, 15))

        # Movement
        self.canvas.bind("<Button-1>", self.start_movement)
        self.canvas.bind("<Motion>", self.movement)
        self.canvas.bind("<ButtonRelease-1>", self.stop_movement)
        self.__move = False

    def spawn_vertex(self):
        vertex = self.canvas.create_oval(30, 30, 105, 105)
        vertex_obj = Vertex(vertex)
        self.vertices.insert(len(self.vertices), vertex_obj)

    def clear_canvas(self, spawn_btn, label_btn, next_btn, connect_btn):
        # Clear all vertex data
        self.vertices.clear()
        self.adjacency_matrix.clear()
        self.canvas.delete('all')

        # Re-enable buttons
        spawn_btn["state"] = "active"
        label_btn["state"] = "active"
        next_btn["state"] = "disabled"
        connect_btn["state"] = "active"

        # Re-bind canvas movement
        self.canvas.bind("<Button-1>", self.start_movement)
        self.canvas.bind("<Motion>", self.movement)
        self.canvas.bind("<ButtonRelease-1>", self.stop_movement)

    def start_movement(self, event):
        global initial_x, initial_y, image_cords, move
        self.__move = True
        initial_x = event.x
        initial_y = event.y
        image_cords = self.canvas.find_closest(initial_x, initial_y, halo=1)

    def stop_movement(self, _event):
        self.__move = False

    def movement(self, event):
        global initial_x, initial_y, image_cords, move
        self.coords_info.config(text="x: " + str(event.x) + ", y: " + str(event.y))
        if self.__move:
            antecedent_x = event.x
            antecedent_y = event.y
            delta_x = antecedent_x - initial_x
            delta_y = antecedent_y - initial_y
            initial_x = antecedent_x
            initial_y = antecedent_y
            self.canvas.move(image_cords, delta_x, delta_y)

    def label_vertices(self, spawn_btn, label_btn, next_btn):
        if len(self.vertices) > 0:
            i = 0
            for x in self.vertices:
                x.name = i
                cords = self.canvas.coords(x.circle)
                self.canvas.create_text((cords[0] + cords[2]) / 2, (cords[1] + cords[3]) / 2, text=i)
                i += 1
            self.canvas.unbind('<Button-1>')
            Application.adjacency_matrix = [[] for _num in range(i)]
            spawn_btn["state"] = "disabled"
            label_btn["state"] = "disabled"
            next_btn["state"] = "active"

    def draw_lines(self):
        if not self.entry_one.get() == "" or not self.entry_two and self.entry_one.get().isdigit() \
                or self.entry_two.get().isdigit():
            first_vertex = self.vertices[int(self.entry_one.get())]
            second_vertex = self.vertices[int(self.entry_two.get())]
            first_cords = self.canvas.coords(first_vertex.circle)
            second_cords = self.canvas.coords(second_vertex.circle)

            self.canvas.create_line(((first_cords[0] + first_cords[2]) / 2),
                                    (first_cords[1] + first_cords[3]) / 2,
                                    ((second_cords[0] + second_cords[2]) / 2),
                                    ((second_cords[1] + second_cords[3]) / 2),
                                    arrow="last")

            self.adjacency_matrix[int(self.entry_one.get())].append(int(self.entry_two.get()))

    def start_thread(self, next_btn, clear_btn, connect_btn):
        next_btn["state"] = "disabled"
        clear_btn["state"] = "disabled"
        connect_btn["state"] = "disabled"
        threading.Thread(target=lambda: self.start_dfs(clear_btn)).start()

    def start_dfs(self, clear_btn):
        visited = [False] * len(self.vertices)
        for i in range(len(self.vertices)):
            if not visited[i]:
                self.dfs(i, visited)
        clear_btn["state"] = "active"

    def dfs(self, s, visited):
        global dfs_time
        dfs_time = 0

        # Create a stack for DFS
        stack = [s]
        finished_stack = []

        while len(stack):
            s = stack[-1]
            stack.pop()
            finished_stack.append(s)

            if not visited[s]:
                time.sleep(2)
                dfs_time += 1
                self.vertices[s].color = "gray"
                self.vertices[s].discovery_time = dfs_time
                self.canvas.itemconfig(self.vertices[s].circle, fill='grey')
                print(s, end=' ')
                visited[s] = True

            for node in self.adjacency_matrix[s]:
                if not visited[node]:
                    self.vertices[node].predecessor = s
                    stack.append(node)

            end = False
            while len(finished_stack) > 0 and not end:
                count = 0
                end = True
                for node in self.adjacency_matrix[finished_stack[-1]]:
                    if visited[node] or len(self.adjacency_matrix[finished_stack[-1]]) == 0:
                        count += 1
                if count == len(self.adjacency_matrix[finished_stack[-1]]):
                    dfs_time += 1
                    end = False
                    time.sleep(2)
                    self.vertices[finished_stack[-1]].finsh_time = dfs_time
                    self.canvas.itemconfig(self.vertices[finished_stack[-1]].circle, fill='black')
                    finished_stack.pop()


if __name__ == "__main__":
    root = Tk()
    Application(root)
    root.mainloop()
