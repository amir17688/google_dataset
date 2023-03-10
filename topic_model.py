"""
Train and apply a topic model to vectorized texts. For example::

    >>> # first, stream a corpus with metadata from disk
    >>> pages = ([pid, title, text] for pid, title, text
    ...          in textacy.corpora.wikipedia.get_plaintext_pages('enwiki-latest-pages-articles.xml.bz2', max_n_pages=100))
    >>> content_stream, metadata_stream = textacy.fileio.read.split_content_and_metadata(pages, 2, itemwise=False)
    >>> metadata_stream = ({'pageid': m[0], 'title': m[1]} for m in metadata_stream)
    >>> corpus = textacy.TextCorpus.from_texts('en', content_stream, metadata=metadata_stream)
    >>> # next, tokenize and vectorize the corpus
    >>> terms_lists = (doc.as_terms_list(words=True, ngrams=False, named_entities=True)
    ...                for doc in corpus)
    >>> doc_term_matrix, id2term = corpus.as_doc_term_matrix(
    ...     terms_lists, weighting='tfidf', normalize=True, smooth_idf=True,
    ...     min_df=3, max_df=0.95, max_n_terms=100000)
    >>> # now initialize and train a topic model
    >>> model = textacy.tm.TopicModel('nmf', n_topics=20)
    >>> model.fit(doc_term_matrix)
    >>> # transform the corpus and interpret our model
    >>> doc_topic_matrix = model.transform(doc_term_matrix)
    >>> for topic_idx, top_terms in model.top_topic_terms(id2term, top_n=10):
    ...     print('topic {}:'.format(topic_idx), '   '.join(top_terms))
    >>> for topic_idx, top_docs in model.top_topic_docs(doc_topic_matrix, top_n=5):
    ...     print('\n{}'.format(topic_idx))
    ...     for j in top_docs:
    ...         print(corpus[j].metadata['title'])
    >>> for doc_idx, topics in model.top_doc_topics(doc_topic_matrix, docs=range(5), top_n=2):
    ...     print('{}: {}'.format(corpus[doc_idx].metadata['title'], topics))
    >>> for i, val in enumerate(model.topic_weights(doc_topic_matrix)):
    ...     print(i, val)
    >>> # assess topic quality through a coherence metric
    >>> # WIP...
    >>> # persist our topic model to disk
    >>> model.save('nmf-20topics.pkl')
"""
import logging
import numpy as np
from sklearn.decomposition import NMF, LatentDirichletAllocation, TruncatedSVD
from sklearn.externals import joblib


logger = logging.getLogger(__name__)


class TopicModel(object):
    """
    Args:
        model ({'nmf', 'lda', 'lsa'} or ``sklearn.decomposition.<model>``)
        n_topics (int, optional): number of topics in the model to be initialized
        kwargs:
            variety of parameters used to initialize the model; see individual
            sklearn pages for full details

    Raises:
        ValueError: if ``model`` not in ``{'nmf', 'lda', 'lsa'}`` or is not an
            NMF, LatentDirichletAllocation, or TruncatedSVD instance

    Notes:
        - http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.NMF.html
        - http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.LatentDirichletAllocation.html
        - http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html
    """
    def __init__(self, model, n_topics=10, **kwargs):
        if isinstance(model, (NMF, LatentDirichletAllocation, TruncatedSVD)):
            self.model = model
        else:
            self.init_model(model, n_topics=n_topics, **kwargs)

    def init_model(self, model, n_topics=10, **kwargs):
        if model == 'nmf':
            self.model = NMF(
                n_components=n_topics,
                alpha=kwargs.get('alpha', 0.1),
                l1_ratio=kwargs.get('l1_ratio', 0.5),
                max_iter=kwargs.get('max_iter', 200),
                random_state=kwargs.get('random_state', 1),
                shuffle=kwargs.get('shuffle', False))
        elif model == 'lda':
            self.model = LatentDirichletAllocation(
                n_topics=n_topics,
                max_iter=kwargs.get('max_iter', 10),
                random_state=kwargs.get('random_state', 1),
                learning_method=kwargs.get('learning_method', 'online'),
                learning_offset=kwargs.get('learning_offset', 10.0),
                batch_size=kwargs.get('batch_size', 128),
                n_jobs=kwargs.get('n_jobs', 1))
        elif model == 'lsa':
            self.model = TruncatedSVD(
                n_components=n_topics,
                algorithm=kwargs.get('algorithm', 'randomized'),
                n_iter=kwargs.get('n_iter', 5),
                random_state=kwargs.get('random_state', 1))
        else:
            msg = 'model "{}" invalid; must be {}'.format(
                model, {'nmf', 'lda', 'lsa'})
            raise ValueError(msg)

    def save(self, filename):
        _ = joblib.dump(self.model, filename, compress=3)
        logger.info('{} model saved to {}'.format(self.model, filename))

    @classmethod
    def load(cls, filename):
        model = joblib.load(filename)
        n_topics = model.n_topics if hasattr(model, 'n_topics') else model.n_components
        return cls(model, n_topics=n_topics)

    def fit(self, doc_term_matrix):
        self.model.fit(doc_term_matrix)

    def partial_fit(self, doc_term_matrix):
        if isinstance(self.model, LatentDirichletAllocation):
            self.model.partial_fit(doc_term_matrix)
        else:
            raise TypeError('only LatentDirichletAllocation models have partial_fit')

    def transform(self, doc_term_matrix):
        return self.model.transform(doc_term_matrix)

    @property
    def n_topics(self):
        try:
            return self.model.n_topics
        except AttributeError:
            return self.model.n_components

    def get_doc_topic_matrix(self, doc_term_matrix, normalize=True):
        """
        Transform a document-term matrix into a document-topic matrix, where rows
        correspond to documents and columns to the topics in the topic model.

        Args:
            doc_term_matrix (array-like or sparse matrix): corpus represented as a
                document-term matrix with shape (n_docs, n_terms); NOTE: LDA expects
                tf-weighting, while NMF and LSA may do better with tfidf-weighting!
            normalize (bool, optional): if True, the values in each row are normalized,
                i.e. topic weights on each document sum to 1

        Returns:
            ``numpy.ndarray``: document-topic matrix with shape (n_docs, n_topics)
        """
        doc_topic_matrix = self.transform(doc_term_matrix)
        if normalize is True:
            return doc_topic_matrix / np.sum(doc_topic_matrix, axis=1, keepdims=True)
        else:
            return doc_topic_matrix

    def top_topic_terms(self, id2term, topics=-1, top_n=10, weights=False):
        """
        Get the top ``top_n`` terms by weight per topic in ``model``.

        Args:
            id2term (list(str) or dict): object that returns the term string corresponding
                to term id ``i`` through ``id2term[i]``; could be a list of strings
                where the index represents the term id, such as that returned by
                ``sklearn.feature_extraction.text.CountVectorizer.get_feature_names()``,
                or a mapping of term id: term string
            topics (int or seq(int), optional): topic(s) for which to return top terms;
                if -1 (default), all topics' terms are returned
            top_n (int, optional): number of top terms to return per topic
            weights (bool, optional): if True, terms are returned with their corresponding
                topic weights; otherwise, terms are returned without weights

        Yields:
            tuple(int, tuple(str)) or tuple(int, tuple((str, float))):
                next tuple corresponding to a topic; the first element is the topic's
                index; if ``weights`` is False, the second element is a tuple of str
                representing the top ``top_n`` related terms; otherwise, the second
                is a tuple of (str, float) pairs representing the top ``top_n``
                related terms and their associated weights wrt the topic; for example::

                    >>> list(TopicModel.top_topic_terms(id2term, topics=(0, 1), top_n=2, weights=False))
                    [(0, ('foo', 'bar')), (1, ('bat', 'baz'))]
                    >>> list(TopicModel.top_topic_terms(id2term, topics=0, top_n=2, weights=True))
                    [(0, (('foo', 0.1415), ('bar', 0.0986)))]
        """
        if topics == -1:
            topics = range(self.n_topics)
        elif isinstance(topics, int):
            topics = (topics,)

        for topic_idx in topics:
            topic = self.model.components_[topic_idx]
            if weights is False:
                yield (topic_idx,
                       tuple(id2term[i] for i in np.argsort(topic)[:-top_n - 1:-1]))
            else:
                yield (topic_idx,
                       tuple((id2term[i], topic[i]) for i in np.argsort(topic)[:-top_n - 1:-1]))

    def top_topic_docs(self, doc_topic_matrix,
                       topics=-1, top_n=10, weights=False):
        """
        Get the top ``top_n`` docs by weight per topic in ``doc_topic_matrix``.

        Args:
            doc_topic_matrix (numpy.ndarray): document-topic matrix with shape
                (n_docs, n_topics), the result of calling
                :func:`get_doc_topic_matrix() <textacy.topic_modeling.get_doc_topic_matrix>`
            topics (seq(int) or int, optional): topic(s) for which to return top docs;
                if -1, all topics' docs are returned
            top_n (int, optional): number of top docs to return per topic
            weights (bool, optional): if True, docs are returned with their corresponding
                (normalized) topic weights; otherwise, docs are returned without weights

        Yields:
            tuple(int, tuple(int)) or tuple(int, tuple(int, float)):
                next tuple corresponding to a topic; the first element is the topic's
                index; if ``weights`` is False, the second element is a tuple of ints
                representing the top ``top_n`` related docs; otherwise, the second
                is a tuple of (int, float) pairs representing the top ``top_n``
                related docs and their associated weights wrt the topic; for example::

                    >>> list(TopicModel.top_doc_terms(dtm, topics=(0, 1), top_n=2, weights=False))
                    [(0, (4, 2)), (1, (1, 3))]
                    >>> list(TopicModel.top_doc_terms(dtm, topics=0, top_n=2, weights=True))
                    [(0, ((4, 0.3217), (2, 0.2154)))]
        """
        if topics == -1:
            topics = range(self.n_topics)
        elif isinstance(topics, int):
            topics = (topics,)

        for topic_idx in topics:
            top_doc_idxs = np.argsort(doc_topic_matrix[:, topic_idx])[:-top_n - 1:-1]
            if weights is False:
                yield (topic_idx,
                       tuple(doc_idx for doc_idx in top_doc_idxs))
            else:
                yield (topic_idx,
                       tuple((doc_idx, doc_topic_matrix[doc_idx, topic_idx]) for doc_idx in top_doc_idxs))

    def top_doc_topics(self, doc_topic_matrix, docs=-1, top_n=3, weights=False):
        """
        Get the top ``top_n`` topics by weight per doc for ``docs`` in ``doc_topic_matrix``.

        Args:
            doc_topic_matrix (numpy.ndarray): document-topic matrix with shape
                (n_docs, n_topics), the result of calling
                :func:`get_doc_topic_matrix() <textacy.topic_modeling.get_doc_topic_matrix>`
            docs (seq(int) or int, optional): docs for which to return top topics;
                if -1, all docs' top topics are returned
            top_n (int, optional): number of top topics to return per doc
            weights (bool, optional): if True, docs are returned with their corresponding
                (normalized) topic weights; otherwise, docs are returned without weights

        Yields:
            tuple(int, tuple(int)) or tuple(int, tuple(int, float)):
                next tuple corresponding to a doc; the first element is the doc's
                index; if ``weights`` is False, the second element is a tuple of ints
                representing the top ``top_n`` related topics; otherwise, the second
                is a tuple of (int, float) pairs representing the top ``top_n``
                related topics and their associated weights wrt the doc; for example::

                    >>> list(TopicModel.top_doc_topics(dtm, docs=(0, 1), top_n=2, weights=False))
                    [(0, (1, 4)), (1, (3, 2))]
                    >>> list(TopicModel.top_doc_topics(dtm, docs=0, top_n=2, weights=True))
                    [(0, ((1, 0.2855), (4, 0.2412)))]
        """
        if docs == -1:
            docs = range(doc_topic_matrix.shape[0])
        elif isinstance(docs, int):
            docs = (docs,)

        for doc_idx in docs:
            top_topic_idxs = np.argsort(doc_topic_matrix[doc_idx, :])[:-top_n - 1:-1]
            if weights is False:
                yield (doc_idx,
                       tuple(topic_idx for topic_idx in top_topic_idxs))
            else:
                yield (doc_idx,
                       tuple((topic_idx, doc_topic_matrix[doc_idx, topic_idx]) for topic_idx in top_topic_idxs))

    def topic_weights(self, doc_topic_matrix):
        """
        Get the overall weight of topics across an entire corpus. Note: Values depend
        on whether topic weights per document in ``doc_topic_matrix`` were normalized,
        or not. I suppose either way makes sense... o_O

        Args:
            doc_topic_matrix (numpy.ndarray): document-topic matrix with shape
                (n_docs, n_topics), the result of calling
                :func:`get_doc_topic_matrix() <textacy.topic_modeling.get_doc_topic_matrix>`

        Returns:
            ``numpy.ndarray``: the ith element is the ith topic's overall weight
        """
        return doc_topic_matrix.sum(axis=0) / doc_topic_matrix.sum(axis=0).sum()

    # def get_topic_coherence(self, topic_idx):
    #     raise NotImplementedError()
    #
    # def get_model_coherence(self):
    #     raise NotImplementedError()
