from cltl.dialogue_evaluation import logger


class BasicEvaluator(object):

    def __init__(self):
        # type: () -> None
        """
        Generate evaluation

        Parameters
        ----------
        """

        self._log = logger.getChild(self.__class__.__name__)
        self._log.info("Booted")

    def evaluate_graph(self, brain):
        raise NotImplementedError()

    def evaluate_response(self, response):
        raise NotImplementedError()
