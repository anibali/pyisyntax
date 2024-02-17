extern "Python" {
  bool python_file_set_pos(int, int64_t);
  int64_t python_file_read_into(int, void*, size_t);
  int64_t python_file_get_size(int);
  void python_file_close(int);
}

/*
Registers Python callback functions for handling I/O operations.
*/
void init_python_platform_utils(
  bool (*python_file_set_pos)(int id, int64_t offset),
  int64_t (*python_file_read_into)(int id, void* dest, size_t bytes_to_read),
  int64_t (*python_file_get_size)(int id),
  void (*python_file_close)(int id)
);
