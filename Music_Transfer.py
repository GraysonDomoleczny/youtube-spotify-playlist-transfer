# YouTube to Spotify Playlist Transfer Tool
#
# This program allows users to transfer a YouTube playlist to Spotify.
#
# Features:
# - Enter Spotify developer credentials to enable full functionality.
# - Input a YouTube playlist URL and choose to add tracks to an existing Spotify playlist or create a new one.
# - When creating a new playlist, prompts for name, description, and visibility settings.
# - Dynamically updates the GUI to show songs being transferred and the remaining count.
#
# Last Updated: 08/21/25


import yt_dlp
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import re
import tkinter as tk
from tkinter import *
from tkinter import ttk


# silences variable warning by setting sp = None
sp: Spotify | None = None

# creates root tkinter window
(root := Tk()).geometry('530x300')
root.title('Youtube > Spotify Playlist Transfer')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
# keeps tkinter window at top of other windows for ease of use
root.attributes('-topmost', True)
# red text style for error messages
style = ttk.Style()
style.configure('Error.TLabel', foreground='red')

# creates main frame in tkinter window which all widgets are placed on
# allows for easy clearing of window by destroying frame after window is used
def CreateFrame():
    # padding and sticky to center frame and add space to edge for appearance
    f = ttk.Frame(root, padding='20 20 20 20')
    f.grid(sticky='n')
    # label stays same size but entry box expands dynamically
    f.columnconfigure(0, weight=0)
    f.columnconfigure(1, weight=1)
    return f

# creates first frame to direct user on how to acquire Spotify credentials
# creates label with corresponding place to input client id and secret
def ClientAuthWindow():
    frame, client_id, client_secret = CreateFrame(), StringVar(), StringVar()
    ttk.Label(frame, text=
        "Due to Spotify's mishandling of quota extension requests, in order to utilize\n"
        "this application you must create an app in Spotify's Developer Dashboard\n"
        "and use the credentials from it to authenticate your account.\n\n"
        "> To do this start by going to https://developer.spotify.com >\n"
        "> Click on the menu top right and choose ‘Log In’ to log in with your Spotify account >\n"
        "> Click the menu again, go to ‘Dashboard’ and choose ‘Create App’ > \n"
        "   - Note: It is advised to make the name and description something recognizable\n"
        "> For the 'Redirect URI' you must use loopback address 'http://127.0.0.1:8888/callback' > \n"
        "> Check the box for ‘Web API’ and Spotify’s 'Developer Terms of Service', then click ‘Save’ >\n"
        "> Click the text ‘View client secret’ and copy and paste your ID and Secret below\n")            .grid(row=0, columnspan=2)
    ttk.Label(frame, text='Client ID')                                                                    .grid(row=1, column=0, sticky='w')
    ttk.Entry(frame, width=70, textvariable=client_id)                                                    .grid(row=1, column=1, padx=10)
    ttk.Label(frame, text='Client Secret')                                                                .grid(row=2, column=0, pady=2)
    ttk.Entry(frame, width=70, textvariable=client_secret)                                                .grid(row=2, column=1, padx=10, pady=2)
    # calls ClientAuth function to process inputted information
    ttk.Button(frame, width=30, text='Enter', command=lambda: ClientAuth(frame, client_id, client_secret)).grid(row=3, columnspan=2, pady=(5, 0))

# checks for missing input or errors in information then assigns values to global sp variable
def ClientAuth(f, cid, cs):
    global sp
    if len(cid.get().strip()) != 32 or len(cs.get().strip()) != 32:
        # gives error message and waits for re-press of button
        for widget in f.grid_slaves(row=4): widget.destroy()
        ttk.Label(f, text='Invalid User ID or Secret', style='Error.TLabel').grid(row=4, columnspan=2)
        return
    # creates and assigns Spotify auth manager using inputted variables
    sp = Spotify(auth_manager = SpotifyOAuth(
        client_id=cid.get().strip(),
        client_secret=cs.get().strip(),
        redirect_uri='http://127.0.0.1:8888/callback',
        # allows reading and modification of all types of playlists
        scope=(
            'playlist-read-private '
            'playlist-read-collaborative '
            'playlist-modify-private '
            'playlist-modify-public')))
    f.destroy(), PlaylistOptionsWindow()

# creates second frame to prompt user for YouTube playlist they want to transfer from
# and if they want to create a new Spotify playlist or add to existing one. if adding select playlists by name
def PlaylistOptionsWindow():
    frame, yt_url, combo, radio = CreateFrame(), StringVar(), StringVar(), StringVar()
    ttk.Label(frame, text='Enter the URL of the playlist on YouTube you want to transfer to Spotify')                    .grid(row=0, columnspan=2)
    ttk.Entry(frame, width=90, textvariable=yt_url)                                                                      .grid(row=1, columnspan=2, pady=5)
    ttk.Label(frame, text='Select one of your Spotify playlists to add to, or create a new playlist')                    .grid(row=2, columnspan=2, pady=(15,0))
    # parallel list of first 9 playlist names on user account and corresponding ids
    playlists = sp.current_user_playlists(limit=9)['items']
    p_name, p_id = [p['name'] for p in playlists], [p['id'] for p in playlists]
    (combo := ttk.Combobox(frame, width=40, textvariable=combo, values=p_name)), combo                                   .grid(row=3, column=0)
    ttk.Radiobutton(frame, text='Add to Playlist', variable=radio, value='add')                                          .grid(row=3, column=1, padx=35, pady=5, sticky='w')
    ttk.Radiobutton(frame, text='Create New Playlist', variable=radio, value='create')                                   .grid(row=4, column=1, padx=35, sticky='w')
    # calls PlaylistOptions function to process inputted information
    ttk.Button(frame, width=45, text='Enter', command=lambda: PlaylistOptions(frame, yt_url, radio, combo, p_name, p_id)).grid(row=5, column=1, padx=(15,0), pady=(25, 0))

# checks for missing or invalid input and passes corresponding error message
# either calls function to create new playlist or passes playlist id to AddSongs function
def PlaylistOptions(f, u, r, c, n, i):
    if 'https://www.youtube.com/playlist?list' not in u.get().strip(): OptionsErrorCheck('Invalid Playlist URL', f)
    elif r.get()=='': OptionsErrorCheck('Select Choice Above', f)
    elif r.get()=='add' and c.get()=='': OptionsErrorCheck('Select Playlist', f)
    # if 'create' selected from radio button passes url to CreatePlaylistWindow
    elif r.get()=='create': f.destroy(), CreatePlaylistWindow(u.get().strip())
    # passes url and playlist id to last function AddSongs
    else:
        playlist_id, url = i[n.index(c.get())], u.get().strip()
        f.destroy(), AddSongs(playlist_id, url)

# called when PlaylistOptions check fails and gives error message
def OptionsErrorCheck(t, f):
    # gives error message and waits for re-press of button
    for widget in f.grid_slaves(row=6, column=1): widget.destroy()
    ttk.Label(f, text=t, style='Error.TLabel').grid(row=6, column=1)
    return

# creates frame to gets input on name, description, and if playlist should be visible on users profile
def CreatePlaylistWindow(u):
    frame, name, description, visibility = CreateFrame(), StringVar(), StringVar(), StringVar()
    ttk.Label(frame, text='Name')                                                                                     .grid(row=0, column=0, sticky='w')
    ttk.Entry(frame, width=75, textvariable=name)                                                                     .grid(row=0, column=1, padx=10)
    ttk.Label(frame, text='Description')                                                                              .grid(row=1, column=0, pady=20)
    ttk.Entry(frame, width=75, textvariable=description)                                                              .grid(row=1, column=1, padx=10)
    ttk.Label(frame, text='Should the playlist be visible on your profile?')                                          .grid(row=2, columnspan=2, pady=5)
    ttk.Radiobutton(frame, text='Yes', variable=visibility, value='True')                                             .grid(row=3, columnspan=2, padx=(0,100))
    ttk.Radiobutton(frame, text='No', variable=visibility, value='False')                                             .grid(row=3, columnspan=2, padx=(100,0))
    # calls CreatePlaylist function to process inputted information
    ttk.Button(frame, width=30, text='Enter', command=lambda: CreatePlaylist(frame, name, description, visibility, u)).grid(row=4, columnspan=2, pady=(20,0))

# checks for missing name or visibility but not missing description and creates Spotify playlist
def CreatePlaylist(f, n, d, v, u):
    if n.get().strip()=='' or v.get()=='':
        # gives error message and waits for re-press of button
        for widget in f.grid_slaves(row=5, column=1): widget.destroy()
        ttk.Label(f, text='Enter Required Information', style='Error.TLabel').grid(row=5, columnspan=2)
        return
    # creates spotify playlist based on inputted information
    created_playlist = sp.user_playlist_create(
        user=sp.current_user()['id'],
        name=n.get().strip(),
        description=d.get().strip(),
        public=v.get()=='True')
    # destroys frame and passes url and newly created playlist id to AddSongs function
    f.destroy(), AddSongs(created_playlist['id'], u)

# creates frame to dynamically display and update counter of songs
# loops through YouTube playlist to get song name and adds song to Spotify playlist
def AddSongs(pid, url):
    frame = CreateFrame()
    ttk.Label(frame, text='-----------------------------------Songs Added-----------------------------------').grid()
    display_song = Text(frame, width=60, height=11); display_song.grid(pady=10)
    # extracts simplified metadata from YouTube playlist and assigns it to variable entries
    entries = yt_dlp.YoutubeDL({'extract_flat': True, 'quiet': True}).extract_info(url, download=False)['entries']

    # uses counter to transfer songs 1 by one in entries and adds top search result to Spotify playlist
    def ProcessNext(index: int):
        if index >= len(entries): ttk.Label(frame, text='Playlist Finished Transferring').grid(); return
        for widget in frame.grid_slaves(row=2): widget.destroy()
        ttk.Label(frame, text=f'{index+1} / {len(entries)}').grid(row=2)
        # strips YouTube title of start and end parentheses for more accurate transfer to Spotify
        title = re.sub(r'\(.*?\)', '', entries[index]['title']).strip()
        # searches YouTube song name on spotify and gets top 20 results
        # due to Spotify search quirks the more results gathered the more accurate but slower the transfer
        track = sp.search(q=title, limit=20, type='track')['tracks']['items'][0]
        # adds song to text box and scrolls to end of text box after each new entry
        display_song.insert(tk.END, f'{track['name']} by {track['artists'][0]['name']}\n')
        display_song.see(tk.END)
        # adds song to Spotify playlist
        sp.playlist_add_items(pid, [track['id']])
        frame.after(100, ProcessNext, index+1)

    #calls function with index 0 to loop through entries
    ProcessNext(0)

# starts tkinter main loop and calls first window to start program
ClientAuthWindow()

root.mainloop()
