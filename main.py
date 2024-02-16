import get_recs as gr
import auth_token_grabber as atg

if __name__=='__main__':
    access_token = atg.main()
    recs = gr.main()


    # Next step is to have a frontend interface
    # Implement some user_input parsing and default config
    # Then have these recommendations post to the front-end