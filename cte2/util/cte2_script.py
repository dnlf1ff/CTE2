import datetime

def _print_cte2():
    print(
            r"""
            (              (
             )\             )
            ((_           /( _
            [  |     )    ))/ |_
             | |--. ((`--((`| |-'_ .--.   _   __
             | .-. |' / .'`\| | [ '/'`\ \[ \ [  ]
             | | | || \__. || |. | \__/ | \ '/ /
            [___]|__]'.__.' \_ / | ;.__/[\_:  /
                              )\ [__|     \__.'
                             (__)

            Starting cte2 ...
            """
            )
    print_time()


def _print_qha():
    print(
            r'''
              ___     _  _      _   
             / _ \   | || |    / \  
            | (_) |  | __ |   / _ \  
             \__\_\  |_||_|  | _ _ |  
            _|"""""|_|"""""|_|"""""| 
            "`-0-0-'"`-0-0-'"`-0-0-'
            Initiating the quasiharmomic approximation module ...
           ''' 
            )
    print_time()

def _print_ppi():
    print(
            f"""

            _  (`-') _  (`-')  _      
              \-.(OO ) \-.(OO ) (_)     
               _.'    \ _.'    \ ,-(`-') 
               (_...--''(_...--'' | ( OO) 
               |  |_.' ||  |_.' | |  |  ) 
               |  .___.'|  .___.'(|  |_/  
               |  |     |  |      |  |'-> 
               `--'     `--'      `--'    

                Initiating the Phonon-phonon Interaction module ... 
            """
            )
    print_time()

def print_time():
    """Print current time."""
    print(
        "-------------------------"
        f"[time {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
        "-------------------------"
        )

def _print_end():
    print("...finished running cte2!")
