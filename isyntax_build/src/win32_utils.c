#include <common.h>
#include <win32_utils.h>

wchar_t* win32_string_widen(const char* s, size_t len, wchar_t* buffer) {
	int characters_written = MultiByteToWideChar(CP_UTF8, 0, s, -1, buffer, len);
	if (characters_written > 0) {
		int last_character = MIN(characters_written, ((int)len)-1);
		buffer[last_character] = '\0';
	} else {
		win32_diagnostic("MultiByteToWideChar");
		buffer[0] = '\0';
	}
	return buffer;
}

char* win32_string_narrow(wchar_t* s, char* buffer, size_t buffer_size) {
	int bytes_written = WideCharToMultiByte(CP_UTF8, 0, s, -1, buffer, buffer_size, NULL, NULL);
	if (bytes_written > 0) {
		ASSERT(bytes_written < buffer_size);
		int last_byte = MIN(bytes_written, ((int)buffer_size)-1);
		buffer[last_byte] = '\0';
	} else {
		win32_diagnostic("WideCharToMultiByte");
		buffer[0] = '\0';
	}
	return buffer;
}

void win32_diagnostic(const char* prefix) {
	DWORD error_id = GetLastError();
	char* message_buffer;
	/*size_t size = */FormatMessageA(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
	                                 NULL, error_id, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), (LPSTR)&message_buffer, 0, NULL);
	console_print("%s: (error code 0x%x) %s\n", prefix, (u32)error_id, message_buffer);
	LocalFree(message_buffer);
}

void win32_diagnostic_verbose(const char* prefix) {
	DWORD error_id = GetLastError();
	char* message_buffer;
	/*size_t size = */FormatMessageA(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
	                                 NULL, error_id, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), (LPSTR)&message_buffer, 0, NULL);
	console_print_verbose("%s: (error code 0x%x) %s\n", prefix, (u32)error_id, message_buffer);
	LocalFree(message_buffer);
}

HANDLE win32_open_overlapped_file_handle(const char* filename) {
	// NOTE: Using the FILE_FLAG_NO_BUFFERING flag *might* be faster, but I am not actually noticing a speed increase,
	// so I am keeping it turned off for now.
	size_t filename_len = strlen(filename) + 1;
	wchar_t* wide_filename = win32_string_widen(filename, filename_len, (wchar_t*) alloca(2 * filename_len));
	HANDLE handle = CreateFileW(wide_filename, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING,
	                            FILE_ATTRIBUTE_NORMAL | /*FILE_FLAG_SEQUENTIAL_SCAN |*/
	                            /*FILE_FLAG_NO_BUFFERING |*/ FILE_FLAG_OVERLAPPED,
	                            NULL);
	return handle;
}
