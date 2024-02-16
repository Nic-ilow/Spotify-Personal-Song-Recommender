import get_recs as gr
import auth_token_grabber as atg
import sys


if __name__=='__main__':
    try:
        playlist_share_link = sys.argv[1]
    except:
        raise Exception("You must provide a share link to your Spotify playlist")
    # playlist_share_link = 'https://open.spotify.com/playlist/5lXcZ1RHv9UPOekkHM4mFO?si=95eb07cc5a654b3f'
    access_token = atg.main()
    recs = gr.main(access_token, playlist_share_link, {})


    # Next step is to have a frontend interface
    # Implement some user_input parsing and default config
    # Then have these recommendations post to the front-end
    print(recs)
