"""``Connector`` objects are responsible for the communication of
information between nodes. Each connector instance is assigned to a
single  node and can be used to send or receive data depending on the
type of connector. ``Output`` connectors are used to send data and
``Input`` objects are used to receive data.
"""

from __future__ import annotations

import multiprocessing as mp
from queue import Empty
from typing import Any, Optional, TYPE_CHECKING, Tuple

from .utils import KillSignal, ObjectCollection
from .exceptions import MissingConnectionError, OverwriteConnectionError

if TYPE_CHECKING:  # pragma: no cover
    from .nodes import AbstractNode


class BaseConnector:
    """Adds signal/slot style functionality to an underlying ``Queue`` object"""

    def __init__(self, name: str = None) -> None:
        """Queue-like object for passing data between nodes

        Args:
            name: Optional human readable name for the connector object
        """

        self.name = str(id(self)) if name is None else name
        self._node: Optional[AbstractNode] = None  # This is the node that this connector is assigned to
        self._connected_partners = ObjectCollection()  # This tracks other connectors that connect to this instance

    @property
    def parent_node(self) -> AbstractNode:
        """The parent node this connector is assigned to"""

        return self._node

    @property
    def partners(self) -> Tuple:
        """Return a tuple of connectors that are connected to this instance"""

        return tuple(self._connected_partners)

    def is_connected(self) -> bool:
        """Return whether the connector has any established connections"""

        return bool(self._connected_partners)

    def __str__(self) -> str:  # pragma: no cover
        return f'<{self.__class__.__name__}(name={self.name}) object at {hex(id(self))}>'


class Input(BaseConnector):
    """Handles the input of data into a pipeline node"""

    def __init__(self, name: str = None, maxsize: int = 0) -> None:
        """Handles the input of data into a pipeline node

        Args:
            name: Optional human readable name for the connector object
            maxsize: The maximum number of communicated items to store in memory
        """

        super().__init__(name=name)
        self._maxsize = maxsize
        self._queue = mp.Queue(maxsize=maxsize)

    def is_empty(self) -> bool:
        """Return if the connection queue is empty"""

        return self._queue.empty()

    def is_full(self) -> bool:
        """Return if the connection queue is full"""

        return self._queue.full()

    def size(self) -> int:
        """Return the size of the connection queue"""

        return self._queue.qsize()

    @property
    def maxsize(self) -> int:
        """The maximum number of objects to store in the connector's memory

        Once the maximum size is reached, the ``put`` method will block until
        an item is moved from the connector into the node.
        """

        return self._queue._maxsize

    @maxsize.setter
    def maxsize(self, maxsize: int) -> None:
        # Replaces the underlying queue with a new instance and updated
        # connected outputs to point at that new instance.

        if not self.is_empty():
            raise RuntimeError('Cannot change maximum connector size when the connector is not empty.')

        self._queue = mp.Queue(maxsize=maxsize)

    def get(self, timeout: Optional[int] = None, refresh_interval: int = 2):
        """Blocking call to retrieve input data

        Releases automatically when no more data is coming from upstream

        Args:
            timeout: Raise a TimeoutError if data is not retrieved within the given number of seconds
            refresh_interval: How often to check if data is expected from upstream

        Raises:
            TimeOutError: Raised if the get call times out
        """

        if not refresh_interval > 0:
            raise ValueError('Connector refresh interval must be greater than zero.')

        timeout = timeout or float('inf')
        while timeout > 0:
            if self.parent_node and not self.parent_node.is_expecting_data():
                return KillSignal

            try:
                return self._queue.get(timeout=min(timeout, refresh_interval))

            except (Empty, TimeoutError):
                timeout -= refresh_interval

        raise TimeoutError

    def iter_get(self) -> Any:
        """Iterator that returns input data

        Automatically exits once no more data is expected from upstream nodes.
        """

        if self.parent_node is None:
            raise MissingConnectionError('Cannot use ``iter_get`` for an ``Input`` not assigned to a parent node.')

        while self.parent_node.is_expecting_data():
            data = self.get()
            if data is KillSignal:
                return

            yield data


class Output(BaseConnector):
    """Handles the output of data from a pipeline node"""

    def __init__(self, name: str = None) -> None:
        """Handles the output of data from a pipeline node

        Args:
            name: Optional human readable name for the connector object
        """

        super().__init__(name=name)
        self._partner: Optional[Input] = None  # The connector object of another node

    def connect(self, connector: Input) -> None:
        """Establish the flow of data between this connector and another connector

        Args:
            connector: The connector object ot connect with
        """

        if type(connector) is type(self):
            raise ValueError('Cannot join together two connection objects of the same type.')

        if connector in self.partners:
            raise OverwriteConnectionError('The given connectors are already connected together.')

        # Once a connection is established between two connectors, they share an internal queue
        self._connected_partners.add(connector)
        connector._connected_partners.add(self)

    def disconnect(self, connector: Input) -> None:
        """Disconnect any established connections"""

        if connector not in self.partners:
            raise MissingConnectionError(f'Output connector is not connected to the given connector: {connector}')

        connector._connected_partners.remove(self)
        self._connected_partners.remove(connector)

    def put(self, x: Any, raise_missing_connection: bool = True) -> None:
        """Add data into the connector

        Args:
            x: The value to put into the connector
            raise_missing_connection: Raise an error if trying to put data into an unconnected output

        Raises:
            MissingConnectionError: If trying to put data into an output that isn't connected to an input
        """

        if not self.is_connected() and raise_missing_connection:
            raise MissingConnectionError('Output connector is not connected to any input connectors.')

        for partner in self.partners:
            partner._queue.put(x)
