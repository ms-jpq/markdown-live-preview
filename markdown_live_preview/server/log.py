from logging import INFO, StreamHandler, getLogger

log = getLogger(__name__)
log.setLevel(INFO)
log.addHandler(StreamHandler())
