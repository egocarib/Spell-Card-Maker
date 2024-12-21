import math
import time


class ProgressBar:
    """
    Utility class for drawing a simple, updating, single-line progress bar
    to the console.
    """
    max: int  # maximum / total number of items to be processed
    wid: int  # character width of progress bar
    cur: int  # current item

    def __init__(self, max_items: int, char_width: int = 30):
        """
        Create a new progress bar object
        :param max_items: The maximum / total number of items to be processed
        :param char_width: The desired width of the progress bar, in characters
        """
        self.max = max_items
        self.wid = char_width
        self.cur = 0

    def increment(self, amt: int = 1):
        """
        Increment the progress bar
        :param amt: The amount to increment by (default: 1)
        """
        self.cur += amt
        if self.cur > self.max:
            self.cur = self.max

    def reset(self, current_ct: int = 0):
        """
        Explicitly set or reset the progress bar
        :param current_ct: The number to reset to (default: 0)
        """
        self.cur = current_ct
        if self.cur > self.max:
            self.cur = self.max

    def draw(self, msg: str, max_msg_len: int = 42):
        """
        Call repeatedly (i.e. in a loop) to draw and update a progress bar. The
        bar will be printed and re-printed to the same console line.
        :param msg: The message to print beside the progress bar. Best to
            keep this short, since everything must fit on one line.
        :param max_msg_len: The max character length of the message. The ``msg``
            parameter will be truncated if it is longer than this.
        :return:
        """
        pct = math.floor(self.cur / self.max * 100)
        pct_str = ('1' if pct == 0 else str(pct)) + '%'
        msg_str = msg.ljust(max_msg_len)[:max_msg_len]
        fill_wid = math.ceil(self.cur * (self.wid / self.max))
        emp_wid = self.wid - fill_wid
        print('▮' * fill_wid + '▯' * emp_wid, pct_str, f'   {msg_str}',
              end='\r')

    def draw_and_increment(self, msg: str, max_msg_len: int = 42, amt: int = 1):
        """
        A shorthand way to call ProgressBar.draw() and ProgressBar.increment()
        :param msg: The message to print beside the progress bar. Best to
            keep this short, since everything must fit on one line.
        :param max_msg_len: The max character length of the message. The ``msg``
            parameter will be truncated if it is longer than this.
        :param amt: The amount to increment by (default: 1)
        """
        self.draw(msg, max_msg_len)
        self.increment(amt)

    def message_and_exit(self, msg: str, delay: float = 0.35):
        """
        Draws the updated progress bar, waits for ``delay`` seconds, and then
        clears the progress bar. A good way to mark that progress is completed
        and remove the progress bar so that your program can continue.
        :param msg: The message to print beside the progress bar. Best to
            keep this short, since everything must fit on one line.
        :param delay: The amount of seconds to wait before clearing the progress
            bar and the specified message.
        """
        self.draw(msg)
        time.sleep(delay)
        self.clear()

    def clear(self):
        """
        Call when finished to clear the progress bar and advance to a new line
        for console output.
        """
        print('\n')
