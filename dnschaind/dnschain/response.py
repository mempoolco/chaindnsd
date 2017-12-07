from dnschaind import add_checksum, base64encode


class Response:
    def __init__(self):
        self._answers = []
        self.ttl = 0
        self.force_ttl = None

    @staticmethod
    def _get_answer_entry(query):
        if query.qtype in [query.available_qtype.TXT]:
            return query.fqdn.replace(query.domain, '.')
        return query.fqdn

    def add_answer(self, query, data: bytes, qtype=None):
        answer = ' '.join(
            [
                self._get_answer_entry(query),
                query.qclass.name,
                qtype is not None and qtype.name or query.qtype.name,
                data
            ]
        )
        self._answers.append(answer)

    @property
    def answers(self):
        return self._answers
