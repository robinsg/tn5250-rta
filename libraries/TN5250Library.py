import subprocess
import time
import os
import datetime
from robot.api import logger

class TN5250Library:
    """
    Robot Framework library for headless TN5250 testing via tmux.
    Supports SSL connections natively.
    """

    def __init__(self, verbose=False):
        """Initialize the TN5250Library.

        Args:
            verbose (bool or str, optional): Enable verbose console output.
                Accepts boolean values or string representations like "true", "1", "yes", "y".
                Defaults to False.

        Returns:
            None
        """
        # Robot may pass boolean-like strings; normalize
        try:
            self.verbose = str(verbose).lower() in ("true", "1", "yes", "y")
        except Exception:
            self.verbose = False
        self.session_name = "robot_tn5250_session"

    def set_verbose(self, verbose=True):
        """Keyword to enable/disable verbose console output.

        Args:
            verbose (bool or str, optional): Enable verbose console output.
                Accepts boolean values or string representations like "true", "1", "yes", "y".
                Defaults to True.

        Returns:
            None

        Examples:
            Set TN5250 Verbose    True
        """
        try:
            self.verbose = str(verbose).lower() in ("true", "1", "yes", "y")
        except Exception:
            self.verbose = False
        logger.info(f"TN5250Library verbose set to {self.verbose}")
        if self.verbose:
            logger.console(f"TN5250Library verbose set to {self.verbose}")

    def _log(self, message):
        """Internal logging method that logs to info and optionally to console.

        Args:
            message (str): The message to log.

        Returns:
            None
        """
        logger.info(message)
        if getattr(self, "verbose", False):
            logger.console(message)

    def start_tn5250_session(self, hostname, ssl, devname=None, map=285):
        """Starts tn5250 in a background tmux session.

        Creates a headless tmux session with standard 80x24 screen dimensions
        and establishes a TN5250 connection to the specified hostname.

        Args:
            hostname (str): The hostname or IP address to connect to.
            ssl (bool or str): If True, connects using SSL ('ssl:hostname' format).
                Accepts boolean values or string representations.
            devname (str, optional): The device name to use for the connection.
                If provided, sets the DEVNAME environment variable. Defaults to None.
            map (int, optional): The character map code to use. Defaults to 285.

        Returns:
            None

        Raises:
            subprocess.CalledProcessError: If tmux session creation fails.
        """
        self.stop_tn5250_session() # Cleanup any old sessions
        
        # Construct the command: 'tn5250 ssl:172.16.8.41'
        prefix = "ssl:" if ssl else ""
        
        cmd = f"tn5250 {prefix}{hostname} map={map}"
        if devname is not None:
            cmd += f" env.DEVNAME={devname}"
        
        self._log(f"Starting session: {cmd}")
        
        # Start headless tmux session (-d) with standard 80x24 screen
        subprocess.run([
            "tmux", "new-session", "-d",
            "-s", self.session_name,
            "-x", "80", "-y", "24",
            cmd
        ], check=True)
        
        time.sleep(3) # Give SSL handshake a moment to finish

    def stop_tn5250_session(self):
        """Kills the tmux session.

        Terminates the active TN5250 tmux session. Errors are silently ignored
        if the session doesn't exist.

        Returns:
            None
        """
        self._log(f"Killing tmux session: {self.session_name}")
        subprocess.run([
            "tmux", "kill-session", "-t", self.session_name
        ], stderr=subprocess.DEVNULL)

    def send_text(self, text):
        """Types text into the terminal.

        Sends the specified text to the active TN5250 session as keyboard input.

        Args:
            text (str): The text to type into the terminal.

        Returns:
            None

        Raises:
            subprocess.CalledProcessError: If sending keys to tmux fails.
        """
        self._log(f"Typing: '{text}'")
        subprocess.run(["tmux", "send-keys", "-t", self.session_name, text], check=True)

    def send_special_key(self, key_name):
        """Sends special keys to the terminal.

        Sends special keys like Enter, Tab, function keys, or Backspace to the
        active TN5250 session. Includes a 0.5 second delay for screen refresh.

        Args:
            key_name (str): The name of the special key to send.
                Examples: "Enter", "Tab", "F3", "Backspace", "F6", etc.

        Returns:
            None

        Raises:
            subprocess.CalledProcessError: If sending keys to tmux fails.
        """
        self._log(f"Sending Key: {key_name}")
        subprocess.run(["tmux", "send-keys", "-t", self.session_name, key_name], check=True)
        time.sleep(0.5) # Wait for screen refresh

    def screen_should_contain(self, expected_text, timeout=10):
        """Waits for text to appear on screen.

        Polls the TN5250 screen content until the expected text is found or
        timeout is reached. If verbose mode is enabled, displays the matching
        screen content. On failure, dumps the final screen content to console.

        Args:
            expected_text (str): The text to search for on the screen.
            timeout (int or str, optional): Maximum time in seconds to wait for
            bool: True if the text is found within the timeout period. This method
            never returns False or None; on timeout it raises an AssertionError.
            never returns False or None; on timeout it raises an AssertionError.

        Returns:
            bool: True if the text is found within the timeout period.

        Raises:
            AssertionError: If the timeout is reached without finding the expected text.
        """
        start_time = time.time()
        while time.time() - start_time < int(timeout):
            # Capture current screen content
            result = subprocess.run([
                "tmux", "capture-pane", "-p", "-t", self.session_name
            ], capture_output=True, text=True)
            if expected_text in result.stdout:
                self._log(f"Found text: '{expected_text}'")
                if self.verbose:
                    # Show the matching screen output for debug
                    logger.console("--- SCREEN (MATCH) ---")
                    logger.console(result.stdout)
                return True
            time.sleep(0.5)
            
        # Log failure
        self._log("--- SCREEN DUMP (FAILURE) ---")
        logger.console(result.stdout)
        raise AssertionError(f"Timeout: Text '{expected_text}' not found on screen.")

    def capture_screen(self, filename=None, image=False):
        """Captures the current TN5250 screen to a text file.

        Saves the current screen content to a text file under `results/screenshots`.
                If None, generates a timestamp-based name like "screen_20231225_120000".
                <timestamp> uses the "%Y%m%d_%H%M%S" format (e.g., "screen_20231225_120000").
                <timestamp> uses the "%Y%m%d_%H%M%S" format (e.g., "screen_20231225_120000").
        the screen as a PNG image.

        Args:
            filename (str, optional): Base name for the output file (without extension).
                If None, generates a timestamp-based name like "screen_20231225_120000".
                Defaults to None.
            image (bool or str, optional): If True, also generate a PNG image of the screen
                using ImageMagick. Accepts boolean values or string representations like
                "true", "1", "yes", "y". Defaults to False.

        Returns:
            str: The full path to the saved text file.

        Raises:
            subprocess.CalledProcessError: If tmux capture-pane fails.
        """
        # Normalize image flag (Robot passes strings sometimes)
        image_flag = False
        try:
            image_flag = str(image).lower() in ("true", "1", "yes", "y")
        except Exception:
            image_flag = False

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Use LPAR-specific screenshot directory if LPAR_NAME is set
        lpar_name = os.environ.get("LPAR_NAME", "")
        if lpar_name:
            out_dir = os.path.join("results", lpar_name, "screenshots")
        else:
            out_dir = os.path.join("results", "screenshots")
        os.makedirs(out_dir, exist_ok=True)

        base = filename if filename else f"screen_{ts}"
        txt_path = os.path.join(out_dir, base + ".txt")

        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(result.stdout)

        self._log(f"Saved screen text to {txt_path}")

        if image_flag:
            png_path = os.path.join(out_dir, base + ".png")
            try:
                proc = subprocess.run(
                    [
                        "convert",
                        "-background",
                        "black",
                        "-fill",
                        "white",
                        "-font",
                        "DejaVu-Sans-Mono",
                        "-pointsize",
                        "12",
                        f"text:{txt_path}",
                        png_path,
                    ],
                    text=True,
                    capture_output=True,
                )
                if proc.returncode == 0:
                    self._log(f"Saved screen image to {png_path}")
                else:
                    self._log(f"ImageMagick convert failed: {proc.stderr}")
            except FileNotFoundError:
                self._log("ImageMagick `convert` not found; skipping image.")

        return txt_path