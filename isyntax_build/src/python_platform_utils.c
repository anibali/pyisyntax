/*
This file is effectively one big hack that implements I/O operations using
Python hooks. This gives more flexibility, as we are no longer restricted to
reading from the local file system only.
*/

#include "common.h"
#include "platform.h"

bool (*_python_file_set_pos)(int id, i64 offset);
i64 (*_python_file_read_into)(int id, void* dest, size_t bytes_to_read);
i64 (*_python_file_get_size)(int id);
void (*_python_file_close)(int id);

void init_python_platform_utils(
  bool (*python_file_set_pos)(int id, i64 offset),
  i64 (*python_file_read_into)(int id, void* dest, size_t bytes_to_read),
  i64 (*python_file_get_size)(int id),
  void (*python_file_close)(int id)
) {
  _python_file_set_pos = python_file_set_pos;
  _python_file_read_into = python_file_read_into;
  _python_file_get_size = python_file_get_size;
  _python_file_close = python_file_close;
}

int platform_stat(const char* filename, struct stat* st) {
  printf("Not implemented.\n");
  exit(1);
}

file_stream_t file_stream_open_for_reading(const char* filename) {
  return (file_stream_t)atoi(filename);
}

file_stream_t file_stream_open_for_writing(const char* filename) {
  printf("Not implemented.\n");
  exit(1);
}

i64 file_stream_read(void* dest, size_t bytes_to_read, file_stream_t file_stream) {
  int id = (int)file_stream;
  return _python_file_read_into(id, dest, bytes_to_read);
}

void file_stream_write(void* source, size_t bytes_to_write, file_stream_t file_stream) {
  printf("Not implemented.\n");
  exit(1);
}

i64 file_stream_get_filesize(file_stream_t file_stream) {
  int id = (int)file_stream;
  return _python_file_get_size(id);
}

i64 file_stream_get_pos(file_stream_t file_stream) {
  printf("Not implemented.\n");
  exit(1);
}

bool file_stream_set_pos(file_stream_t file_stream, i64 offset) {
  int id = (int)file_stream;
  return _python_file_set_pos(id, offset);
}

void file_stream_close(file_stream_t file_stream) {
}

file_handle_t open_file_handle_for_simultaneous_access(const char* filename) {
  return (file_handle_t)atoi(filename);
}

void file_handle_close(file_handle_t file_handle) {
  int id = (int)file_handle;
  _python_file_close(id);
}

size_t file_handle_read_at_offset(void* dest, file_handle_t file_handle, u64 offset, size_t bytes_to_read) {
  int id = (int)file_handle;
  _python_file_set_pos(id, offset);
  i64 read = _python_file_read_into(id, dest, bytes_to_read);
  return read;
}
