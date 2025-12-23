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
        # Robot may pass boolean-like strings; normalize
        try:
            self.verbose = str(verbose).lower() in ("true", "1", "yes", "y")
        except Exception:
            self.verbose = False
        self.session_name = "robot_tn5250_session"

    def set_verbose(self, verbose=True):
        """Keyword to enable/disable verbose console output.

        Usage: `Set TN5250 Verbose    True`
        """
        try:
            self.verbose = str(verbose).lower() in ("true", "1", "yes", "y")
        except Exception:
            self.verbose = False
        logger.info(f"TN5250Library verbose set to {self.verbose}")
        if self.verbose:
            logger.console(f"TN5250Library verbose set to {self.verbose}")

    def _log(self, message):
        logger.info(message)
        if getattr(self, "verbose", False):
            logger.console(message)

    def start_tn5250_session(self, hostname, ssl, devname=None, map=285):
        """
        Starts tn5250 in a background tmux session.
        If ssl is True, connects using 'ssl:hostname'.
        If devname not equal None then use the specifies device name.
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
        """Kills the tmux session."""
        self._log(f"Killing tmux session: {self.session_name}")
        subprocess.run([
            "tmux", "kill-session", "-t", self.session_name
        ], stderr=subprocess.DEVNULL)

    def send_text(self, text):
        """Types text into the terminal."""
        self._log(f"Typing: '{text}'")
        subprocess.run(["tmux", "send-keys", "-t", self.session_name, text], check=True)

    def send_special_key(self, key_name):
        """Sends special keys: Enter, Tab, F3, Backspace."""
        self._log(f"Sending Key: {key_name}")
        subprocess.run(["tmux", "send-keys", "-t", self.session_name, key_name], check=True)
        time.sleep(0.5) # Wait for screen refresh

    def screen_should_contain(self, expected_text, timeout=10):
        """
        Waits for text to appear. Fails if timeout is reached.
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
        """
        Captures the current TN5250 screen to a text file under `results/screenshots`.
        If `image` is truthy and ImageMagick `convert` is available, also renders a PNG.
        Returns the path to the text file.
        """
        # Normalize image flag (Robot passes strings sometimes)
        image_flag = False
        try:
            image_flag = str(image).lower() in ("true", "1", "yes", "y")
        except Exception:
            image_flag = False

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
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
                        "label:@-",
                        png_path,
                    ],
                    input=result.stdout,
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

    def _get_screen_content(self):
        """
        Internal helper to get current screen content.
        
        Returns:
            str: Current screen content
            
        Raises:
            RuntimeError: If tmux command fails
        """
        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to capture screen: {result.stderr}")
        
        return result.stdout

    def _get_screen_lines(self):
        """
        Internal helper to get screen content as list of lines.
        
        Returns:
            list: List of screen lines
        """
        content = self._get_screen_content()
        return content.split('\n')

    def search_line(self, line_number, search_text):
        """
        Search for text on a specific line of the TN5250 display.
        
        Args:
            line_number: Line number to search (1-24)
            search_text: Text to search for
            
        Returns:
            bool: True if text found on line, False otherwise
        """
        lines = self._get_screen_lines()
        line_idx = int(line_number) - 1  # Convert to 0-based index
        
        if line_idx < 0 or line_idx >= len(lines):
            self._log(f"Line {line_number} is out of range")
            return False
        
        found = search_text in lines[line_idx]
        self._log(f"Search line {line_number} for '{search_text}': {found}")
        if self.verbose:
            logger.console(f"Line {line_number}: {lines[line_idx]}")
        return found

    def get_line_text(self, line_number, start_col=1, length=None):
        """
        Retrieve text from a specific line on the TN5250 display.
        
        Args:
            line_number: Line number to read (1-24)
            start_col: Starting column (1-80), default 1
            length: Number of characters to retrieve, None for rest of line
            
        Returns:
            str: Text from the specified line
        """
        lines = self._get_screen_lines()
        line_idx = int(line_number) - 1  # Convert to 0-based index
        col_idx = int(start_col) - 1  # Convert to 0-based index
        
        if line_idx < 0 or line_idx >= len(lines):
            raise ValueError(f"Line {line_number} is out of range")
        
        line = lines[line_idx]
        
        if length is None:
            text = line[col_idx:]
        else:
            text = line[col_idx:col_idx + int(length)]
        
        self._log(f"Get line {line_number} text from col {start_col}: '{text}'")
        return text

    def search_display(self, search_text):
        """
        Search for text anywhere on the TN5250 display.
        
        Args:
            search_text: Text to search for
            
        Returns:
            bool: True if text found on display, False otherwise
        """
        content = self._get_screen_content()
        found = search_text in content
        self._log(f"Search display for '{search_text}': {found}")
        return found

    def get_text_at_position(self, row, column, length):
        """
        Retrieve text of given length from specific row and column.
        
        Args:
            row: Row number (1-24)
            column: Column number (1-80)
            length: Number of characters to retrieve
            
        Returns:
            str: Text from the specified position
        """
        lines = self._get_screen_lines()
        row_idx = int(row) - 1  # Convert to 0-based index
        col_idx = int(column) - 1  # Convert to 0-based index
        
        if row_idx < 0 or row_idx >= len(lines):
            raise ValueError(f"Row {row} is out of range")
        
        line = lines[row_idx]
        text = line[col_idx:col_idx + int(length)]
        
        self._log(f"Get text at row {row}, col {column}, length {length}: '{text}'")
        return text

    def search_two_strings(self, first_string, second_string):
        """
        Search for two strings on the display and return which were found.
        
        Args:
            first_string: First string to search for
            second_string: Second string to search for
            
        Returns:
            str: One of "both", "first", "second", or "neither"
        """
        content = self._get_screen_content()
        first_found = first_string in content
        second_found = second_string in content
        
        if first_found and second_found:
            result = "both"
        elif first_found:
            result = "first"
        elif second_found:
            result = "second"
        else:
            result = "neither"
        
        self._log(f"Search two strings '{first_string}' and '{second_string}': {result}")
        return result

    def get_block_text(self, start_row, start_col, end_row, end_col):
        """
        Retrieve a block of text from start position to end position.
        
        Args:
            start_row: Starting row (1-24)
            start_col: Starting column (1-80)
            end_row: Ending row (must be >= start_row + 1)
            end_col: Ending column (must be >= start_col)
            
        Returns:
            str: Text from the specified block
        """
        start_row = int(start_row)
        start_col = int(start_col)
        end_row = int(end_row)
        end_col = int(end_col)
        
        # Validate constraints
        if end_row < start_row + 1:
            raise ValueError(f"end_row ({end_row}) must be >= start_row + 1 ({start_row + 1})")
        if end_col < start_col:
            raise ValueError(f"end_col ({end_col}) must be >= start_col ({start_col})")
        
        lines = self._get_screen_lines()
        result_lines = []
        
        for row in range(start_row, end_row + 1):
            row_idx = row - 1  # Convert to 0-based index
            
            if row_idx < 0 or row_idx >= len(lines):
                continue
            
            line = lines[row_idx]
            
            if row == start_row:
                # First line: start from start_col
                if row == end_row:
                    # Single line span
                    result_lines.append(line[start_col - 1:end_col])
                else:
                    result_lines.append(line[start_col - 1:])
            elif row == end_row:
                # Last line: end at end_col
                result_lines.append(line[:end_col])
            else:
                # Middle lines: full line
                result_lines.append(line)
        
        text = '\n'.join(result_lines)
        self._log(f"Get block text from ({start_row},{start_col}) to ({end_row},{end_col})")
        return text

    def search_block(self, start_row, start_col, end_row, end_col, search_text):
        """
        Search for text within a specific block of the display.
        
        Args:
            start_row: Starting row (1-24)
            start_col: Starting column (1-80)
            end_row: Ending row (must be >= start_row + 1)
            end_col: Ending column (must be >= start_col)
            search_text: Text to search for
            
        Returns:
            bool: True if text found in block, False otherwise
        """
        block_text = self.get_block_text(start_row, start_col, end_row, end_col)
        found = search_text in block_text
        self._log(f"Search block ({start_row},{start_col})-({end_row},{end_col}) for '{search_text}': {found}")
        return found

    def get_message_line(self):
        """
        Read the TN5250 message line (line 24).
        
        Returns:
            str: Text from line 24
        """
        lines = self._get_screen_lines()
        if len(lines) >= 24:
            message = lines[23]  # 0-based index for line 24
            self._log(f"Message line: '{message}'")
            return message
        else:
            self._log("Message line not available")
            return ""