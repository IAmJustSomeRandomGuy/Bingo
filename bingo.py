import PySimpleGUI as sg
import random
from math import floor
from settings import *

json_file_text = []
json_exists = False

try:
  json_file = open("bingo.json", 'r')
  json_file_text = json_file.read()
  json_file.close()
  
  json_file_text = json_file_text.split('"},\n{"name": "')
  json_file_text[0] = json_file_text[0][11:]
  json_file_text[-1] = json_file_text[-1][:-3]

  if len(json_file_text) == 25:
    json_exists = True

except FileNotFoundError:
  print('Found no file: bingo.json (this is only used for sharing a bingo board without the code and objectives.txt)')
except:
  print('bingo.py file has probably wrong formating (or another issue)')

quests_file = open("objectives.txt", "r")
quest_file_text = quests_file.read().split('\n')
empty_items = quest_file_text.count('')
for x in range(empty_items):
  quest_file_text.remove('')

difficulty_of_quest = -1
group = ''
quest_dict = {}
bingo_size = 5
bingo_code = ''
box_size = 6
keep_json_file_checked = False

for x in quest_file_text:
  if 'bingo_size ='.upper()  in x.upper():
    bingo_size = int(x[-1])
    bingo_code += x[-1] + ';'
  elif 'box_size ='.upper() in x.upper():
    box_size = int(x[-1])
  elif 'keep_json_file_checked = True'.upper() in x.upper():
    keep_json_file_checked = True
  elif ' objectives:'.upper() in x.upper():
    x = x[:-12]
    if x not in quest_dict.keys():
      quest_dict[x] = []
    group = x
  elif group != '':
    quest_dict[group].append(x)

  
quests_file.close()
all_quests = []
all_groups = []

for x in quest_dict.values():
  all_quests += x
for x in quest_dict.keys():
  all_groups += [x]

bingo_code += str(len(all_quests)) + ';'

board = [['' for _ in range(bingo_size)] for _ in range(bingo_size)]
board_completed = board.copy()
playing = False

for x in range(bingo_size):
  completed_row = []
  for y in range(bingo_size):
    completed_row += [False]
  board_completed[x] = completed_row

all_groups_middle = floor(len(all_groups)/2)

def makeBingoBoard(difficulty):
  global bingo_code
  quest_list = quest_dict[all_groups[difficulty]]
  original_difficulty = difficulty
  decrease = False
    
  board = [['' for _ in range(bingo_size)] for _ in range(bingo_size)]
  picked_quests = []

  while len(picked_quests) < bingo_size**2:
    if len(quest_list) == 0:
      if ((len(all_groups)-1) > difficulty) and (not decrease):
        difficulty += 1
        quest_list = quest_dict[all_groups[difficulty]]

        print('increasing difficulty since not enough quests/objectives')
      elif (len(all_groups)-1) <= difficulty:
        difficulty = original_difficulty
        decrease = True

        print('resetting difficulty to original')
      elif decrease and difficulty >= 0:
        difficulty -= 1
        quest_list = quest_dict[all_groups[difficulty]]

        print('decreasing difficulty since not enough quests/objectives')
      else:
        raise ValueError('NOT ENOUGH QUESTS/OBJETIVES!!!')       
    
    if len(quest_list) != 0:
      random_quest = random.randint(0,len(quest_list)-1)

      quest = quest_list[random_quest]
      quest_list.remove(quest)
      picked_quests += [quest]
      
  random.shuffle(picked_quests)

  for x in picked_quests:
      bingo_code += str(all_quests.index(x)) + ';'
  
  # probably not needed board
  i = 0
  for x in range(bingo_size):
    for y in range(bingo_size):
      board[x][y] = picked_quests[i]
      i += 1
      window[(x,y)].update(board[x][y])
      
  window["-CODE-"].update(bingo_code)

  if bingo_size == 5 and values['-JSON-']:
    JSON_file = open('bingo.json', 'w')
    JSON_content = '['
    for x in picked_quests:
      JSON_content += '{"name": "'+x+'"},\n'
    JSON_content = JSON_content[:-2]
    JSON_content += ']'
    JSON_file.write(JSON_content)

  window['-SELECTION-'].update(visible=False)
  window['-BINGO-'].update(visible=True)
  window['-BINGO-'].expand(expand_row=True, expand_y=True)

def importJSON():
  global bingo_code

  board = [['' for _ in range(bingo_size)] for _ in range(bingo_size)]

  try:
    for x in json_file_text:
      bingo_code += str(all_quests.index(x)) + ';'
  except ValueError:
    bingo_code = "Could not generate bingo code (json file objectives aren't in objectives.txt)"
    window['-CODE-'].update(text_color='red')

  window["-CODE-"].update(bingo_code)
  
  # probably not needed board
  i = 0
  for x in range(bingo_size):
    for y in range(bingo_size):
      board[x][y] = json_file_text[i]
      i += 1
      window[(x,y)].update(board[x][y])

  window['-SELECTION-'].update(visible=False)
  window['-BINGO-'].update(visible=True)
  window['-BINGO-'].expand(expand_row=True, expand_y=True)



column_size = (18*box_size*bingo_size, window_size[1])

# title screen
home = [
  [sg.Canvas(s=(column_size[0],0), pad=(0,0), background_color=main_color_2)],
  [sg.Text("Bingo", background_color=main_color_2)],
  [sg.Text("", background_color=main_color_2)],
  [sg.Button("Start", mouseover_colors=main_color_3, k="-START BUTTON-", size=(20,4))]
]

# difficulty selection
difficulty_selection = [
  [sg.Canvas(s=(column_size[0],0), pad=(0,0), background_color=main_color_2)],
  [sg.Text("select bingo difficulty:", background_color=main_color_2)],
  [sg.Text("", background_color=main_color_2)]
]

if bingo_size == 5 and keep_json_file_checked:
  difficulty_selection += [
    [sg.Checkbox("create JSON file for bingosync", background_color=main_color_2, k='-JSON-', default=True)],
    [sg.Text("", background_color=main_color_2)]
  ]
elif bingo_size == 5:
    difficulty_selection += [
  [sg.Checkbox("create JSON file for bingosync", background_color=main_color_2, k='-JSON-')],
  [sg.Text("", background_color=main_color_2)]
]

# generates difficulties
for x in all_groups:
  difficulty_selection += [
    [sg.Button(x, mouseover_colors=main_color_3, k=x, size=(20, 4))],
    [sg.Text("", background_color=main_color_2)]
  ]

if json_exists and bingo_size == 5:
  difficulty_selection += [
    [sg.Button('Import from bingo.json', mouseover_colors=main_color_3, k='json', size=(20, 4))],
    [sg.Text("", background_color=main_color_2)]
  ]

# custom button and sliders
# if len(all_groups) > 1:
#   difficulty_selection += [
#     # [sg.Slider(range=(0, bingo_size-1), orientation='h', s=(15, 20), k='-'+x.upper()+' SLIDER-' ) for x in all_groups],
#     [sg.Slider(range=(0, bingo_size-1), enable_events=True, orientation='h', s=(15, 20), k='-'+str(x)+' SLIDER-' ) for x in range(len(all_groups)-1)],
#     [sg.Button('Costum', mouseover_colors=main_color_3, k='-CUSTOM-', size=(20, 4))]
#   ]

# code input
difficulty_selection += [
  [sg.Text("", background_color=main_color_2)],
  [sg.Input("", k="-CODE INPUT-", background_color=main_color_1, tooltip='input code'), sg.Button('-SUBMIT CODE-', bind_return_key=True, visible=False)],
  [sg.Text("", background_color=main_color_2)]
]

# bingo board
bingo_board = [
  [sg.Button(board[i][j], size=(box_size*2, box_size), key=(i,j)) for j in range(bingo_size)] for i in range(bingo_size)
]

bingo_board += [
  [sg.Text('Bingo code: ', background_color=main_color_2)],
  [sg.Input(bingo_code, k="-CODE-", readonly=True, disabled_readonly_background_color=main_color_2)],
  [sg.Text("", background_color=main_color_2)]
]

# content
layout = [
  [sg.Column(home, k='-START-', background_color=main_color_2, expand_y=True, element_justification='center'), sg.Column(difficulty_selection, k='-SELECTION-', background_color=main_color_2, expand_y=True, visible=False, element_justification='center', vertical_alignment='c'), sg.Column(bingo_board, k='-BINGO-', background_color=main_color_2, expand_y=True, visible=False, vertical_alignment='c'),]
]

# making a window
window = sg.Window("WOL Bingo", layout=layout, size=window_size, background_color=bg_color, button_color=main_color_1, default_button_element_size=(300,3), element_padding=(0,0), element_justification='c')


# event loop
while True:
  event, values = window.read()
  # print(event, values)
  
  if event == sg.WIN_CLOSED:
    break
  
  if event == "-START BUTTON-":
    window['-START-'].update(visible=False)
    window['-SELECTION-'].update(visible=True)
    window['-SELECTION-'].expand(expand_row=True, expand_y=True)
    # window['-'+str(all_groups_middle)+' SLIDER-'].update(value=bingo_size-1)
    # for x in range(len(all_groups)-1):
    #   if all_groups_middle > x:
    #     window['-'+str(x)+' SLIDER-'].update(range=(0, 1))
    #     window['-'+str(x)+' SLIDER-'].set_size((None, 50))
    #   elif all_groups_middle == x:
    #     window['-'+str(x)+' SLIDER-'].update(range=(0, bingo_size-len(all_groups)+1))
    #     window['-'+str(x)+' SLIDER-'].set_size((None, (bingo_size-len(all_groups))*50))
    #   else:
    #     window['-'+str(x)+' SLIDER-'].update(range=(0, 1), value=2)
    #     window['-'+str(x)+' SLIDER-'].set_size((None, 50))

    window['-CODE INPUT-'].set_focus(force=True)
    window['-CODE-'].expand(expand_row=True, expand_x=True)
  
  # enter code
  if event == "-SUBMIT CODE-" and len(values['-CODE INPUT-']) > 5:
    submitted_code = values['-CODE INPUT-'].split(';')
    if '' in submitted_code:
      submitted_code.remove('')
    submitted_code = list(map(int, submitted_code))

    # checks if code is functional
    if submitted_code[0]**2 == len(submitted_code)-2 and submitted_code[1] == len(all_quests):
      bingo_size = submitted_code[0]
      board = [['' for _ in range(bingo_size)] for _ in range(bingo_size)]

      i = 2
      for x in range(bingo_size):
        for y in range(bingo_size):
          board[x][y] = all_quests[submitted_code[i]]
          i += 1
          window[(x,y)].update(board[x][y])

      window["-CODE-"].update(submitted_code)
      
      window['-SELECTION-'].update(visible=False)
      window['-BINGO-'].update(visible=True)
      window['-BINGO-'].expand(expand_row=True, expand_y=True)
    else:
      window['-CODE INPUT-'].update('WRONG CODE or objectives.txt', text_color='red')
      print('ERROR')
  
  for i, x in enumerate(all_groups):
    if event == x:
      difficulty = i
      makeBingoBoard(difficulty)
      # if window['-SELECTION-'].get_size()[1] > window_size[1]:
      #   pass
      playing = True
    # if event == '-'+str(i)+' SLIDER-':
    #   pass
  
  if event == 'json':
    importJSON()

  if playing == True and type(event) is tuple:
    if board_completed[event[0]][event[1]] == False:
      window[event].update(button_color=('green'))
      board_completed[event[0]][event[1]] = True
    elif board_completed[event[0]][event[1]] == True:
      window[event].update(button_color=main_color_1)
      board_completed[event[0]][event[1]] = False

print(bingo_code)

window.close()