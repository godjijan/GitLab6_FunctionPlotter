#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Лабораторная работа №6. Построение и анализ графиков функций.
Выполнил: Студент группы 25-ПИЭ Стаценко С.М.
Проверил: проф. каф. инф. тех., д.т.н. Попов Д.И.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
# Используем TkAgg бэкенд для интеграции Matplotlib в окно Tkinter
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class PlotAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор графиков функций — Лабораторная работа №6")
        self.root.geometry("1200x800")
        self.root.minimum_size = (1000, 700)
        
        # Стилизация интерфейса с помощью ttk
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Список для хранения добавленных графиков
        # Каждая запись: {"id": int, "type": str, "A": float, "B": float, "color": str, "visible": bool}
        self.graphs = []
        self.graph_id_counter = 1
        
        # Цветовая палитра для графиков по умолчанию
        self.available_colors = ["blue", "green", "red", "orange", "purple", "brown", "magenta", "cyan"]
        
        # Инициализация интерфейса
        self.create_widgets()
        
        # Построение начального пустого координатного пространства
        self.plot_graphs()

    def create_widgets(self):
        """Создание всех элементов управления и области рисования"""
        # Главный контейнер (разделение на панель управления и график)
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая панель параметров и списков (со скроллбаром при необходимости)
        left_frame = ttk.Frame(main_paned, width=400)
        left_frame.pack(fill=tk.BOTH, expand=True)
        main_paned.add(left_frame, weight=1)
        
        # Правая панель для графика Matplotlib
        right_frame = ttk.Frame(main_paned)
        right_frame.pack(fill=tk.BOTH, expand=True)
        main_paned.add(right_frame, weight=2)
        
        # --- ЛЕВАЯ ПАНЕЛЬ: Элементы управления ---
        
        # 1. Границы отображения (X1, X2, Y1, Y2)
        window_frame = ttk.LabelFrame(left_frame, text=" Границы окна отображения ")
        window_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(window_frame, text="X1 (Мин):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_x1 = ttk.Entry(window_frame, width=8)
        self.entry_x1.insert(0, "-10")
        self.entry_x1.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(window_frame, text="X2 (Макс):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.entry_x2 = ttk.Entry(window_frame, width=8)
        self.entry_x2.insert(0, "10")
        self.entry_x2.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(window_frame, text="Y1 (Мин):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_y1 = ttk.Entry(window_frame, width=8)
        self.entry_y1.insert(0, "-10")
        self.entry_y1.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(window_frame, text="Y2 (Макс):").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.entry_y2 = ttk.Entry(window_frame, width=8)
        self.entry_y2.insert(0, "10")
        self.entry_y2.grid(row=1, column=3, padx=5, pady=5)
        
        btn_update_limits = ttk.Button(window_frame, text="Применить границы", command=self.update_limits)
        btn_update_limits.grid(row=2, column=0, columnspan=4, pady=8, sticky=tk.EW, padx=5)

        # 2. Форма добавления графика
        add_frame = ttk.LabelFrame(left_frame, text=" Добавить график функции ")
        add_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(add_frame, text="Выберите функцию:").pack(anchor=tk.W, padx=5, pady=2)
        self.func_select = ttk.Combobox(add_frame, state="readonly", values=[
            "y = A * sin(B * x)",
            "y = A * cos(B * x)",
            "y = A * x + B (Линейная)",
            "y = A * x^2 + B * x (Квадратичная)",
            "y = A * exp(B * x) (Экспонента)",
            "y = A * ln(B * x) (Логарифм)"
        ])
        self.func_select.current(0)
        self.func_select.pack(fill=tk.X, padx=5, pady=2)
        
        # Коэффициенты A и B
        coeff_frame = ttk.Frame(add_frame)
        coeff_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(coeff_frame, text="Параметр A:").grid(row=0, column=0, padx=2, pady=5, sticky=tk.W)
        self.entry_a = ttk.Entry(coeff_frame, width=10)
        self.entry_a.insert(0, "1.0")
        self.entry_a.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(coeff_frame, text="Параметр B:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.entry_b = ttk.Entry(coeff_frame, width=10)
        self.entry_b.insert(0, "1.0")
        self.entry_b.grid(row=0, column=3, padx=2, pady=5)
        
        # Выбор цвета
        color_frame = ttk.Frame(add_frame)
        color_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(color_frame, text="Цвет линии:").pack(side=tk.LEFT, padx=2)
        self.color_select = ttk.Combobox(color_frame, width=12, state="readonly", values=self.available_colors)
        self.color_select.current(0)
        self.color_select.pack(side=tk.LEFT, padx=5)
        
        btn_add_graph = ttk.Button(add_frame, text="Добавить функцию в список", command=self.add_graph)
        btn_add_graph.pack(fill=tk.X, padx=5, pady=8)
        
        # 3. Список активных графиков
        list_frame = ttk.LabelFrame(left_frame, text=" Список активных графиков ")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.graphs_listbox = tk.Listbox(list_frame, height=5, selectmode=tk.SINGLE)
        self.graphs_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.graphs_listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.graphs_listbox.config(yscrollcommand=list_scrollbar.set)
        
        # Кнопки управления списком
        btn_list_frame = ttk.Frame(left_frame)
        btn_list_frame.pack(fill=tk.X, padx=10, pady=2)
        
        btn_delete_graph = ttk.Button(btn_list_frame, text="Удалить выбранный", command=self.delete_graph)
        btn_delete_graph.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        btn_clear_graphs = ttk.Button(btn_list_frame, text="Очистить все", command=self.clear_graphs)
        btn_clear_graphs.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # 4. Вычисление корней уравнения F1(x) = F2(x) для выбранной пары
        roots_frame = ttk.LabelFrame(left_frame, text=" Вычисление корней F1(x) = F2(x) ")
        roots_frame.pack(fill=tk.X, padx=10, pady=5)
        
        pair_frame = ttk.Frame(roots_frame)
        pair_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(pair_frame, text="F1:").grid(row=0, column=0, padx=2, pady=2, sticky=tk.W)
        self.combo_f1 = ttk.Combobox(pair_frame, state="readonly", width=15)
        self.combo_f1.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(pair_frame, text="F2:").grid(row=0, column=2, padx=2, pady=2, sticky=tk.W)
        self.combo_f2 = ttk.Combobox(pair_frame, state="readonly", width=15)
        self.combo_f2.grid(row=0, column=3, padx=5, pady=2)
        
        btn_calc_roots = ttk.Button(roots_frame, text="Найти точки пересечения (корни)", command=self.show_roots)
        btn_calc_roots.pack(fill=tk.X, padx=5, pady=5)
        
        self.txt_roots = tk.Text(roots_frame, height=4, width=40, state=tk.DISABLED, wrap=tk.WORD)
        self.txt_roots.pack(fill=tk.X, padx=5, pady=5)
        
        # --- ПРАВАЯ ПАНЕЛЬ: Координатная плоскость ---
        # Создаем контейнер для Matplotlib и встраиваем его
        self.fig = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True, which='both', linestyle='--', alpha=0.7)
        self.ax.axhline(y=0, color='k', linestyle='-', linewidth=1.2)
        self.ax.axvline(x=0, color='k', linestyle='-', linewidth=1.2)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.draw()
        
        # Добавление навигационной панели (для масштабирования и перемещения)
        self.toolbar = NavigationToolbar2Tk(self.canvas, right_frame)
        self.toolbar.update()
        
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # --- МАТЕМАТИЧЕСКАЯ ЛОГИКА ОЦЕНКИ ФУНКЦИЙ ---
    
    def evaluate_function(self, func_type, A, B, x):
        """
        Вычисляет значение у для массива numpy x.
        Предотвращает переполнение и некорректные математические операции.
        """
        if func_type == "y = A * sin(B * x)":
            return A * np.sin(B * x)
        elif func_type == "y = A * cos(B * x)":
            return A * np.cos(B * x)
        elif func_type == "y = A * x + B (Линейная)":
            return A * x + B
        elif func_type == "y = A * x^2 + B * x (Квадратичная)":
            return A * (x ** 2) + B * x
        elif func_type == "y = A * exp(B * x) (Экспонента)":
            # Безопасное возведение в степень во избежание переполнения (overflow)
            bx = B * x
            bx_clipped = np.clip(bx, -100, 100)
            return A * np.exp(bx_clipped)
        elif func_type == "y = A * ln(B * x) (Логарифм)":
            bx = B * x
            # Логарифм определен только для положительных аргументов
            with np.errstate(divide='ignore', invalid='ignore'):
                return np.where(bx > 0, A * np.log(bx), np.nan)
        return np.zeros_like(x)

    def evaluate_function_single(self, func_type, A, B, x):
        """Вычисляет значение у для одного числа x"""
        if func_type == "y = A * sin(B * x)":
            return A * np.sin(B * x)
        elif func_type == "y = A * cos(B * x)":
            return A * np.cos(B * x)
        elif func_type == "y = A * x + B (Линейная)":
            return A * x + B
        elif func_type == "y = A * x^2 + B * x (Квадратичная)":
            return A * (x ** 2) + B * x
        elif func_type == "y = A * exp(B * x) (Экспонента)":
            bx = B * x
            if bx > 100: bx = 100
            if bx < -100: bx = -100
            return A * np.exp(bx)
        elif func_type == "y = A * ln(B * x) (Логарифм)":
            bx = B * x
            if bx <= 0:
                return float('nan')
            return A * np.log(bx)
        return 0.0

    # --- ПОИСК КОРНЕЙ И ТОЧЕК ПЕРЕСЕЧЕНИЯ ---
    
    def find_roots(self, g1, g2, x1, x2, tol=1e-5, grid_points=1000):
        """
        Находит корни уравнения g1(x) - g2(x) = 0 на интервале [x1, x2]
        Используется метод сканирования сетки в сочетании с методом деления пополам (дихотомии).
        Это гарантирует обнаружение всех корней без зависимости от внешних решателей SciPy.
        """
        xs = np.linspace(x1, x2, grid_points)
        roots = []
        
        def diff(x):
            try:
                y1 = self.evaluate_function_single(g1["type"], g1["A"], g1["B"], x)
                y2 = self.evaluate_function_single(g2["type"], g2["A"], g2["B"], x)
                if np.isnan(y1) or np.isnan(y2) or np.isinf(y1) or np.isinf(y2):
                    return None
                return y1 - y2
            except:
                return None

        # Шаг 1: Поиск интервалов смены знака функции разности
        for i in range(len(xs) - 1):
            xa, xb = xs[i], xs[i+1]
            ya, yb = diff(xa), diff(xb)
            
            if ya is None or yb is None:
                continue
            
            if ya * yb <= 0:
                # Шаг 2: Метод деления пополам на локальном отрезке [xa, xb]
                a, b = xa, xb
                for _ in range(60):  # Лимит итераций для точности
                    mid = (a + b) / 2.0
                    ymid = diff(mid)
                    if ymid is None:
                        break
                    if abs(ymid) < tol:
                        roots.append(mid)
                        break
                    
                    # Проверяем у какого подинтервала разные знаки
                    ya_temp = diff(a)
                    if ya_temp is None:
                        break
                    if ya_temp * ymid <= 0:
                        b = mid
                    else:
                        a = mid
                else:
                    roots.append((a + b) / 2.0)
                    
        # Фильтрация дубликатов с учетом погрешности
        unique_roots = []
        for r in roots:
            if not any(abs(r - ur) < 1e-4 for ur in unique_roots):
                # Дополнительная проверка на действительность точки (не является ли она асимптотой)
                yval1 = self.evaluate_function_single(g1["type"], g1["A"], g1["B"], r)
                yval2 = self.evaluate_function_single(g2["type"], g2["A"], g2["B"], r)
                if not np.isnan(yval1) and not np.isinf(yval1):
                    unique_roots.append(r)
                    
        return sorted(unique_roots)

    # --- ИНТЕРФЕЙСНЫЕ КОМАНДЫ ---

    def parse_axis_limits(self):
        """Читает и проверяет границы координатной области."""
        values = [
            float(self.entry_x1.get()), float(self.entry_x2.get()),
            float(self.entry_y1.get()), float(self.entry_y2.get())
        ]
        if not all(np.isfinite(value) for value in values):
            raise ValueError("Границы должны быть конечными числами.")
        x1, x2, y1, y2 = values
        if x1 >= x2 or y1 >= y2:
            raise ValueError("Минимальная граница должна быть меньше максимальной.")
        return x1, x2, y1, y2

    def update_limits(self):
        """Применяет проверенные настройки масштаба окна к осям."""
        try:
            self.parse_axis_limits()
            self.plot_graphs()
        except ValueError as error:
            messagebox.showerror("Ошибка ввода", f"Некорректные границы:\n{error}")

    def add_graph(self):
        """Добавляет новый график функции в список на основе полей ввода"""
        try:
            func_type = self.func_select.get()
            A = float(self.entry_a.get())
            B = float(self.entry_b.get())
            color = self.color_select.get()

            if not np.isfinite(A) or not np.isfinite(B):
                raise ValueError("Коэффициенты A и B должны быть конечными числами.")

            # Валидация
            if func_type == "y = A * ln(B * x) (Логарифм)" and B == 0:
                raise ValueError("Для логарифма параметр B не должен быть равен 0.")
                
            graph_data = {
                "id": self.graph_id_counter,
                "type": func_type,
                "A": A,
                "B": B,
                "color": color,
                "visible": True
            }
            self.graphs.append(graph_data)
            self.graph_id_counter += 1
            
            # Обновление списков интерфейса
            self.update_graphs_listbox()
            self.update_comboboxes_for_roots()
            
            # Автоматическая смена цвета для следующего графика
            next_color_index = (self.color_select.current() + 1) % len(self.available_colors)
            self.color_select.current(next_color_index)
            
            self.plot_graphs()
        except ValueError as e:
            messagebox.showerror("Ошибка параметров", f"Ошибка при разборе параметров функции:\n{e}")

    def delete_graph(self):
        """Удаляет выбранную из списка функцию"""
        selected_index = self.graphs_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Внимание", "Пожалуйста, выберите функцию из списка для удаления.")
            return
            
        idx = selected_index[0]
        self.graphs.pop(idx)
        
        # Перерисовка и обновление выпадающих списков
        self.update_graphs_listbox()
        self.update_comboboxes_for_roots()
        self.plot_graphs()

    def clear_graphs(self):
        """Удаляет все функции после подтверждения пользователя."""
        if not self.graphs:
            messagebox.showinfo("Список пуст", "Нет графиков для удаления.")
            return
        if not messagebox.askyesno("Подтверждение", "Удалить все добавленные графики?"):
            return
        self.graphs.clear()
        self.graph_id_counter = 1
        self.update_graphs_listbox()
        self.update_comboboxes_for_roots()
        self.plot_graphs()

    def update_graphs_listbox(self):
        """Обновляет текстовый список функций на экране"""
        self.graphs_listbox.delete(0, tk.END)
        for g in self.graphs:
            display_text = f"F{g['id']}: {g['type'].split(' (')[0]} [A={g['A']}, B={g['B']}] — {g['color']}"
            self.graphs_listbox.insert(tk.END, display_text)

    def update_comboboxes_for_roots(self):
        """Обновляет элементы выбора пары графиков для вычисления корней"""
        options = [f"F{g['id']}" for g in self.graphs]
        self.combo_f1["values"] = options
        self.combo_f2["values"] = options
        
        if len(options) >= 1:
            self.combo_f1.current(0)
        else:
            self.combo_f1.set("")
            
        if len(options) >= 2:
            self.combo_f2.current(1)
        elif len(options) == 1:
            self.combo_f2.current(0)
        else:
            self.combo_f2.set("")

    def get_graph_by_label(self, label):
        """Возвращает словарь данных графика по его метке типа 'F1'"""
        if not label:
            return None
        try:
            g_id = int(label[1:])
            for g in self.graphs:
                if g["id"] == g_id:
                    return g
        except:
            return None
        return None

    def show_roots(self):
        """Считает корни F1(x) = F2(x) и выводит их в текстовое поле"""
        lbl1 = self.combo_f1.get()
        lbl2 = self.combo_f2.get()
        
        if not lbl1 or not lbl2:
            messagebox.showwarning("Предупреждение", "Для поиска корней необходимо добавить хотя бы 2 графика!")
            return
            
        if lbl1 == lbl2:
            messagebox.showwarning("Предупреждение", "Выберите две РАЗЛИЧНЫЕ функции!")
            return
            
        g1 = self.get_graph_by_label(lbl1)
        g2 = self.get_graph_by_label(lbl2)
        
        if not g1 or not g2:
            return
            
        try:
            x1 = float(self.entry_x1.get())
            x2 = float(self.entry_x2.get())
        except:
            x1, x2 = -10, 10
            
        # Нахождение корней на видимом интервале
        roots = self.find_roots(g1, g2, x1, x2)
        
        # Вывод результатов в текстовое поле
        self.txt_roots.config(state=tk.NORMAL)
        self.txt_roots.delete("1.0", tk.END)
        
        if not roots:
            self.txt_roots.insert(tk.END, f"Корней уравнения {lbl1}(x) = {lbl2}(x) на интервале [{x1}, {x2}] не обнаружено.")
        else:
            self.txt_roots.insert(tk.END, f"Корни {lbl1}(x) = {lbl2}(x) на [{x1}, {x2}]:\n")
            for i, r in enumerate(roots, 1):
                y_val = self.evaluate_function_single(g1["type"], g1["A"], g1["B"], r)
                self.txt_roots.insert(tk.END, f" x{i} = {r:.5f}  ==>  y = {y_val:.5f}\n")
                
        self.txt_roots.config(state=tk.DISABLED)
        
        # Акцентируем внимание на графике: перерисуем и подсветим именно эти корни
        self.plot_graphs(highlight_pair_roots=(g1, g2, roots))

    # --- ВИЗУАЛИЗАЦИЯ (ОТРИСОВКА В MATPLOTLIB) ---

    def plot_graphs(self, highlight_pair_roots=None):
        """Очищает и полностью перерисовывает координатную плоскость"""
        self.ax.clear()
        
        # Получаем проверенные границы окна отображения
        try:
            x1, x2, y1, y2 = self.parse_axis_limits()
        except ValueError:
            x1, x2, y1, y2 = -10, 10, -10, 10
            
        # Установка сетки и осей координат
        self.ax.grid(True, which='both', linestyle='--', alpha=0.5)
        self.ax.axhline(y=0, color='black', linestyle='-', linewidth=1.2)
        self.ax.axvline(x=0, color='black', linestyle='-', linewidth=1.2)
        
        # Генерация плотного набора точек X для качественного рендеринга без ступенек
        # Используем 1000 точек
        x_pts = np.linspace(x1, x2, 1000)
        
        # Отрисовка всех активных функций
        for g in self.graphs:
            y_pts = self.evaluate_function(g["type"], g["A"], g["B"], x_pts)
            
            # Маскируем невалидные точки (например, NaN для логарифма)
            mask = np.isfinite(y_pts)
            
            clean_x = x_pts[mask]
            clean_y = y_pts[mask]
            
            label_text = f"F{g['id']}: {g['type'].split(' (')[0]} (A={g['A']}, B={g['B']})"
            self.ax.plot(clean_x, clean_y, label=label_text, color=g["color"], linewidth=2)
            
        # --- АВТОМАТИЧЕСКИЙ ПОИСК ВСЕХ ТОЧЕК ПЕРЕСЕЧЕНИЯ ДЛЯ ВСЕХ ПАР ---
        # Если графиков больше одного, ищем попарные пересечения
        all_intersection_points = []
        if len(self.graphs) >= 2:
            for i in range(len(self.graphs)):
                for j in range(i + 1, len(self.graphs)):
                    g1 = self.graphs[i]
                    g2 = self.graphs[j]
                    pts = self.find_roots(g1, g2, x1, x2)
                    for px in pts:
                        py = self.evaluate_function_single(g1["type"], g1["A"], g1["B"], px)
                        if y1 <= py <= y2: # Только видимые на экране точки
                            all_intersection_points.append((px, py, g1["id"], g2["id"]))
                            
        # Наносим все точки пересечения на график в виде красных маркеров
        for px, py, id1, id2 in all_intersection_points:
            self.ax.plot(px, py, marker='o', color='red', markersize=6)
            # Добавим текстовую аннотацию рядом с точкой пересечения
            self.ax.annotate(f"({px:.2f}, {py:.2f})",
                             xy=(px, py),
                             xytext=(10, 5),
                             textcoords='offset points',
                             fontsize=8,
                             bbox=dict(boxstyle="round,pad=0.2", fc="yellow", alpha=0.5))
            
        # Если была выбрана конкретная пара для анализа корней, подсветим их по-особому (например, звездочками)
        if highlight_pair_roots:
            g1, g2, roots = highlight_pair_roots
            for rx in roots:
                ry = self.evaluate_function_single(g1["type"], g1["A"], g1["B"], rx)
                if y1 <= ry <= y2:
                    self.ax.plot(rx, ry, marker='*', color='gold', markeredgecolor='black', markersize=12, label="Выбранный корень")

        # Принудительная фиксация границ осей
        self.ax.set_xlim(x1, x2)
        self.ax.set_ylim(y1, y2)
        
        # Настройка красивых подписей осей
        self.ax.set_xlabel('Ось X', fontsize=11)
        self.ax.set_ylabel('Ось Y', fontsize=11)
        self.ax.set_title('Графический анализатор пересечений функций', fontsize=12, fontweight='bold')
        
        # Показываем легенду, если есть хотя бы один график
        if self.graphs:
            self.ax.legend(loc='best', fontsize=9)
            
        # Обновляем холст
        self.canvas.draw()

# Точка входа в программу
if __name__ == "__main__":
    root = tk.Tk()
    app = PlotAnalyzerApp(root)
    root.mainloop()