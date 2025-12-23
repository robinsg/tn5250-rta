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

    def search_text_on_line(self, line_number, search_text):
        """
        Search for a string of data on a specific line on the TN5250 display.
        Returns True if the text exists on that line, False otherwise.
        
        Args:
            line_number: The line number to search (1-24)
            search_text: The text to search for
            
        Returns:
            True if text is found on the specified line, False otherwise
        """
        line_num = int(line_number)
        if line_num < 1 or line_num > 24:
            raise ValueError(f"Line number must be between 1 and 24, got {line_num}")
            
        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to capture screen: {result.stderr}")
            
        lines = result.stdout.split('\n')
        if line_num <= len(lines):
            line_content = lines[line_num - 1]
            found = search_text in line_content
            self._log(f"Search on line {line_num}: '{search_text}' - {'FOUND' if found else 'NOT FOUND'}")
            return found
        
        self._log(f"Line {line_num} not available in screen output")
        return False

    def retrieve_text_from_line(self, line_number, start_column, length):
        """
        Retrieve a specific length of string data from a specific line.
        
        Args:
            line_number: The line number to read from (1-24)
            start_column: Starting column position (1-80)
            length: Number of characters to retrieve
            
        Returns:
            The retrieved text string
        """
        line_num = int(line_number)
        start_col = int(start_column)
        text_length = int(length)
        
        if line_num < 1 or line_num > 24:
            raise ValueError(f"Line number must be between 1 and 24, got {line_num}")
        if start_col < 1 or start_col > 80:
            raise ValueError(f"Start column must be between 1 and 80, got {start_col}")
            
        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to capture screen: {result.stderr}")
            
        lines = result.stdout.split('\n')
        if line_num <= len(lines):
            line_content = lines[line_num - 1]
            # Convert to 0-based indexing
            start_idx = start_col - 1
            end_idx = start_idx + text_length
            retrieved = line_content[start_idx:end_idx]
            self._log(f"Retrieved from line {line_num}, col {start_col}, length {text_length}: '{retrieved}'")
            return retrieved
        
        raise RuntimeError(f"Line {line_num} not available in screen output")

    def search_text_on_screen(self, search_text):
        """
        Search for a string of data anywhere on the TN5250 display.
        Returns True if the text exists on the screen, False otherwise.
        
        Args:
            search_text: The text to search for
            
        Returns:
            True if text is found on screen, False otherwise
        """
        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to capture screen: {result.stderr}")
            
        found = search_text in result.stdout
        self._log(f"Search on screen: '{search_text}' - {'FOUND' if found else 'NOT FOUND'}")
        return found

    def retrieve_text_from_position(self, row, column, length):
        """
        Retrieve data of a given length from a given TN5250 row and column number.
        
        Args:
            row: Row number (1-24)
            column: Column number (1-80)
            length: Number of characters to retrieve
            
        Returns:
            The retrieved text string
        """
        # This is essentially the same as retrieve_text_from_line
        return self.retrieve_text_from_line(row, column, length)

    def search_two_texts_on_screen(self, first_text, second_text):
        """
        Look for two different string values anywhere on the TN5250 display.
        
        Args:
            first_text: First string to search for
            second_text: Second string to search for
            
        Returns:
            String indicating which texts were found:
            - "both" if both strings are found
            - "first_only" if only the first string is found
            - "second_only" if only the second string is found
            - "neither" if neither string is found
        """
        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to capture screen: {result.stderr}")
            
        first_found = first_text in result.stdout
        second_found = second_text in result.stdout
        
        if first_found and second_found:
            outcome = "both"
        elif first_found:
            outcome = "first_only"
        elif second_found:
            outcome = "second_only"
        else:
            outcome = "neither"
            
        self._log(f"Search two texts: '{first_text}' and '{second_text}' - Result: {outcome}")
        return outcome

    def retrieve_text_block(self, start_row, start_column, end_row, end_column):
        """
        Retrieve a block of TN5250 display data from a given starting row/column
        to a given ending row/column.
        
        Args:
            start_row: Starting row number (1-24)
            start_column: Starting column number (1-80)
            end_row: Ending row number (must be >= start_row + 1)
            end_column: Ending column number (must be >= start_column)
            
        Returns:
            The retrieved text block as a string with newlines preserved
        """
        start_r = int(start_row)
        start_c = int(start_column)
        end_r = int(end_row)
        end_c = int(end_column)
        
        # Validate inputs
        if start_r < 1 or start_r > 24:
            raise ValueError(f"Start row must be between 1 and 24, got {start_r}")
        if end_r < 1 or end_r > 24:
            raise ValueError(f"End row must be between 1 and 24, got {end_r}")
        if start_c < 1 or start_c > 80:
            raise ValueError(f"Start column must be between 1 and 80, got {start_c}")
        if end_c < 1 or end_c > 80:
            raise ValueError(f"End column must be between 1 and 80, got {end_c}")
        if end_r < start_r + 1:
            raise ValueError(f"End row must be at least start row + 1 (end: {end_r}, start: {start_r})")
        if end_c < start_c:
            raise ValueError(f"End column must be >= start column (end: {end_c}, start: {start_c})")
            
        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to capture screen: {result.stderr}")
            
        lines = result.stdout.split('\n')
        block_lines = []
        
        for row_num in range(start_r, end_r + 1):
            if row_num <= len(lines):
                line = lines[row_num - 1]
                # For first and last rows, extract the specific column range
                if row_num == start_r:
                    # First row - from start_column to end of line
                    block_lines.append(line[start_c - 1:])
                elif row_num == end_r:
                    # Last row - from start of line to end_column
                    block_lines.append(line[:end_c])
                else:
                    # Middle rows - take full line
                    block_lines.append(line)
        
        block_text = '\n'.join(block_lines)
        self._log(f"Retrieved block from ({start_r},{start_c}) to ({end_r},{end_c})")
        return block_text

    def search_text_in_block(self, start_row, start_column, end_row, end_column, search_text):
        """
        Search for text within a block of TN5250 display data.
        
        Args:
            start_row: Starting row number (1-24)
            start_column: Starting column number (1-80)
            end_row: Ending row number (must be >= start_row + 1)
            end_column: Ending column number (must be >= start_column)
            search_text: Text to search for within the block
            
        Returns:
            True if text is found in the block, False otherwise
        """
        block = self.retrieve_text_block(start_row, start_column, end_row, end_column)
        found = search_text in block
        self._log(f"Search in block ({start_row},{start_column}) to ({end_row},{end_column}): '{search_text}' - {'FOUND' if found else 'NOT FOUND'}")
        return found

    def retrieve_message_line(self):
        """
        Read the TN5250 message line (line 24) to retrieve informational and error information.
        
        Returns:
            The content of line 24 (the message line)
        """
        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to capture screen: {result.stderr}")
            
        lines = result.stdout.split('\n')
        if len(lines) >= 24:
            message = lines[23]  # 0-based index
            self._log(f"Message line (24): '{message}'")
            return message
        
        self._log("Message line (24) not available")
        return ""