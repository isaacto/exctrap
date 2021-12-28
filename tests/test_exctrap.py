from unittest.mock import call, patch

import exctrap
import pytest


def test_exc_trapper_normal() -> None:
    trapper = exctrap.ExcTrapper()
    a = 10
    with trapper:
        a = 20
    assert a == 20
    trapper.reraise()


def test_exc_trapper_raises() -> None:
    trapper = exctrap.ExcTrapper()
    with trapper:
        raise RuntimeError('foo')
    assert str(trapper.exc[0]) == 'foo'
    with pytest.raises(RuntimeError):
        trapper.reraise()


def test_trial_normal() -> None:
    lst: typing.List[int] = []
    for cnt, etrapper in enumerate(exctrap.trial()):
        with etrapper:
            lst.append(cnt)
    assert lst == [0]


def test_trial_raises_nomock() -> None:
    lst: typing.List[int] = []
    with pytest.raises(RuntimeError):
        for cnt, etrapper in enumerate(exctrap.trial(retry_period=0)):
            with etrapper:
                lst.append(cnt)
                raise RuntimeError()
    assert lst == list(range(3))


def test_trial_raises_mock_sleep_nonoise() -> None:
    lst: typing.List[int] = []
    with patch('time.sleep') as mock_sleep:
        with pytest.raises(RuntimeError):
            for cnt, etrapper in enumerate(exctrap.trial(retry_period=0.1,
                                                         period_noise=0)):
                with etrapper:
                    lst.append(cnt)
                    raise RuntimeError()
    assert mock_sleep.mock_calls == [call(0.1), call(0.1)]
    assert lst == list(range(3))


def test_trial_raises_mock_sleep_noisy() -> None:
    lst: typing.List[int] = []
    with patch('time.sleep') as mock_sleep:
        with pytest.raises(RuntimeError):
            for cnt, etrapper in enumerate(exctrap.trial(num_tries=1000,
                                                         retry_period=2,
                                                         period_noise=0.5)):
                with etrapper:
                    lst.append(cnt)
                    raise RuntimeError()
    assert len(mock_sleep.mock_calls) == 999
    found_small, found_large = False, False
    for call in mock_sleep.mock_calls:
        arg = call[1][0]
        assert 1 <= arg <= 3
        if arg < 1.1:
            found_small = True
        if arg > 2.9:
            found_large = True
    assert found_small and found_large


def test_trial_raises_mock_sleep_backoff() -> None:
    lst: typing.List[int] = []
    with patch('time.sleep') as mock_sleep:
        with pytest.raises(RuntimeError):
            for cnt, etrapper in enumerate(exctrap.trial(6,
                                                         retry_period=1.,
                                                         period_noise=0,
                                                         backoff=2)):
                with etrapper:
                    lst.append(cnt)
                    raise RuntimeError()
    assert mock_sleep.mock_calls == [call(1.), call(2.), call(4.),
                                     call(4.), call(4.)]
    assert lst == list(range(6))
