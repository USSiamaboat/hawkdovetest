import streamlit as st
import copy
import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt

@st.cache
def once():
    st.set_page_config(layout='wide')

once()

options, info = st.beta_columns([1, 3])

death = 0.05

dove_dist = 0.95

count = 100000

ticks = 20

dove_log = []
hawk_log = []

class Bird:
    hawk = 0  # 0 = dove, 1 = hawk
    food = 0

def reset_board():
    out = []
    hawks = np.concatenate([np.zeros(int(np.round(count*dove_dist))), np.ones(int(np.round(count*(1-dove_dist))))])
    for i in range(count):
        new_bird = Bird()
        new_bird.food = 0
        new_bird.hawk = hawks[i]
        out.append(new_bird)
    st.session_state.board = out

def meet():
    board_ = st.session_state.board
    board = copy.deepcopy(board_)
    out_board = []
    if len(board) % 2 == 1:
        board.pop()
    
    while len(board) != 0:
        player1_i = np.random.randint(0, len(board))
        player1 = board[player1_i]
        board.pop(player1_i)
        player2_i = np.random.randint(0, len(board))
        player2 = board[player2_i]
        
        if player1.hawk == 1:
            if player2.hawk == 1:
                player1.food += 0.25
                player2.food += 0.25
            else:
                player1.food += 1.5
                player2.food += 0.5
        else:
            if player2.hawk == 1:
                player1.food += 0.5
                player2.food += 1.5
            else:
                player1.food += 1
                player2.food += 1
        
        out_board.append(player1)
        out_board.append(player2)
        board.pop(player2_i)
    st.session_state.board = out_board

def judgement():
    global death
    board_ = st.session_state.board
    board = copy.deepcopy(board_)
    out_board = []
    
    print(len(board))
    
    for i, bird in enumerate(board):
        if random.random() >= death/bird.food:
            bird.food = 0
            out_board.append(bird)
    
    if len(out_board) <= 500:
        doves = 0
        hawks = 0
        for bird in board:
            if bird.hawk == 1:
                hawks += 1
            else:
                doves += 1
        
        total = doves+hawks
        dove_prop = doves/total
        hawks_prop = hawks/total
        hawk_ = np.concatenate([
            np.zeros(int(np.round(dove_prop*200))),
            np.ones(int(np.round(hawks_prop * 200)))
        ])
        for i in range(200):
            new_bird = Bird()
            new_bird.hawk = hawk_[i]
            out_board.append(new_bird)
    
    st.session_state.board = out_board

def log():
    global hawk_log
    global dove_log
    hawk_count = 0
    dove_count = 0
    
    board = st.session_state.board
    
    for bird in board:
        if bird.hawk == 1:
            hawk_count += 1
        else:
            dove_count += 1
    
    hawk_log.append(hawk_count)
    dove_log.append(dove_count)

def tick():
    meet()
    judgement()
    log()

def game():
    global ticks
    global hawk_log
    global dove_log
    
    reset_board()
    for i in range(ticks):
        print("------------")
        print("tick "+str(i))
        tick()
    
    proportion_dove = []
    
    for i in range(len(hawk_log)):
        total = hawk_log[i] + dove_log[i]
        if total == 0:
            break
        proportion_dove.append(dove_log[i]/total)
    with info:
        st.write(pd.DataFrame([
            range(len(proportion_dove)),
            proportion_dove
        ]))
        fig, ax = plt.subplots()
        ax.plot(list(range(len(proportion_dove))), proportion_dove)
        st.pyplot(fig)

with options:
    if "board" not in st.session_state:
        reset_board()
    
    ticks = st.slider("Ticks", 1, 200, ticks, 1)
    
    death = st.slider("Death", 0.00, 1.00, death, 0.05)
    
    dove_dist = st.slider("Dove Distribution", 0.0, 1.0, dove_dist, 0.05)
    
    st.button("Run", on_click=game)
