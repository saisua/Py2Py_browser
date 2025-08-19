python -m coverage run -m unittest \
    encryption/tests/* \
    && \
coverage report

# python -m coverage run -m unittest \
#     communication/tests/* \
#     db/tests/* \
#     encryption/tests/* \
#     models/tests/* \
#     utils/tests/* \
#     && \
# coverage report
