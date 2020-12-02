from datetime import datetime, timezone

import numpy as np
import pandas as pd

from suncalc import get_position, get_times

date = datetime(2013, 3, 5, tzinfo=timezone.utc)
lat = 50.5
lng = 30.5
height = 2000

testTimes = {
    'solar_noon': '2013-03-05T10:10:57Z',
    'nadir': '2013-03-04T22:10:57Z',
    'sunrise': '2013-03-05T04:34:56Z',
    'sunset': '2013-03-05T15:46:57Z',
    'sunrise_end': '2013-03-05T04:38:19Z',
    'sunset_start': '2013-03-05T15:43:34Z',
    'dawn': '2013-03-05T04:02:17Z',
    'dusk': '2013-03-05T16:19:36Z',
    'nautical_dawn': '2013-03-05T03:24:31Z',
    'nautical_dusk': '2013-03-05T16:57:22Z',
    'night_end': '2013-03-05T02:46:17Z',
    'night': '2013-03-05T17:35:36Z',
    'golden_hour_end': '2013-03-05T05:19:01Z',
    'golden_hour': '2013-03-05T15:02:52Z'}

heightTestTimes = {
    'solar_noon': '2013-03-05T10:10:57Z',
    'nadir': '2013-03-04T22:10:57Z',
    'sunrise': '2013-03-05T04:25:07Z',
    'sunset': '2013-03-05T15:56:46Z'}


def test_get_position():
    """getPosition returns azimuth and altitude for the given time and location
    """
    pos = get_position(date, lng, lat)
    assert np.isclose(pos['azimuth'], -2.5003175907168385)
    assert np.isclose(pos['altitude'], -0.7000406838781611)


def test_get_times():
    """getTimes returns sun phases for the given date and location
    """
    times = get_times(date, lng, lat)
    for key, value in testTimes.items():
        assert times[key].strftime("%Y-%m-%dT%H:%M:%SZ") == value


def test_get_times_height():
    """getTimes adjusts sun phases when additionally given the observer height
    """
    times = get_times(date, lng, lat, height)
    for key, value in heightTestTimes.items():
        assert times[key].strftime("%Y-%m-%dT%H:%M:%SZ") == value


def test_get_position_pandas_single_timestamp():
    ts_date = pd.Timestamp(date)

    pos = get_position(ts_date, lng, lat)
    assert np.isclose(pos['azimuth'], -2.5003175907168385)
    assert np.isclose(pos['altitude'], -0.7000406838781611)


def test_get_position_pandas_datetime_series():
    df = pd.DataFrame({'date': [date] * 3, 'lat': [lat] * 3, 'lng': [lng] * 3})

    pos = pd.DataFrame(get_position(df['date'], df['lng'], df['lat']))

    assert pos.shape == (3, 2)
    assert all(x in pos.columns for x in ['azimuth', 'altitude'])
    assert pos.dtypes['azimuth'] == np.dtype('float64')
    assert pos.dtypes['altitude'] == np.dtype('float64')

    assert np.isclose(pos['azimuth'].iloc[0], -2.5003175907168385)
    assert np.isclose(pos['altitude'].iloc[0], -0.7000406838781611)


def test_get_times_pandas_single():
    times = get_times(date, lng, lat)

    assert isinstance(times['solar_noon'], pd.Timestamp)


def test_get_times_datetime_single():
    times = get_times(date, lng, lat)

    # This is true because pd.Timestamp is an instance of datetime.datetime
    assert isinstance(times['solar_noon'], datetime)


def test_get_times_arrays():
    df = pd.DataFrame({'date': [date] * 3, 'lat': [lat] * 3, 'lng': [lng] * 3})

    times = pd.DataFrame(get_times(df['date'], df['lng'], df['lat']))

    assert pd.api.types.is_datetime64_any_dtype(times['solar_noon'])

    assert times['solar_noon'].iloc[0].strftime(
        "%Y-%m-%dT%H:%M:%SZ") == testTimes['solar_noon']


def test_get_times_for_high_latitudes():
    """getTimes may fail (maybe only on Windows?) for high latitudes in the summer

    See https://github.com/kylebarron/suncalc-py/issues/4
    """
    date = datetime(2020, 5, 26, 0, 0, 0)
    lng = -114.0719
    lat = 51.0447

    # Make sure this doesn't raise an exception (though it will emit a warning
    # due to a division error)
    times = get_times(date, lng, lat)


# t.test('getMoonPosition returns moon position data given time and location', function (t) {
#     var moonPos = SunCalc.getMoonPosition(date, lng, lat);
#
#     t.ok(near(moonPos.azimuth, -0.9783999522438226), 'azimuth');
#     t.ok(near(moonPos.altitude, 0.014551482243892251), 'altitude');
#     t.ok(near(moonPos.distance, 364121.37256256194), 'distance');
#     t.end();
# });
#
# t.test('getMoonIllumination returns fraction and angle of moon\'s illuminated limb and phase', function (t) {
#     var moonIllum = SunCalc.getMoonIllumination(date);
#
#     t.ok(near(moonIllum.fraction, 0.4848068202456373), 'fraction');
#     t.ok(near(moonIllum.phase, 0.7548368838538762), 'phase');
#     t.ok(near(moonIllum.angle, 1.6732942678578346), 'angle');
#     t.end();
# });
#
# t.test('getMoonTimes returns moon rise and set times', function (t) {
#     var moonTimes = SunCalc.getMoonTimes(new Date('2013-03-04UTC'), lng, lat, true);
#
#     t.equal(moonTimes.rise.toUTCString(), 'Mon, 04 Mar 2013 23:54:29 GMT');
#     t.equal(moonTimes.set.toUTCString(), 'Mon, 04 Mar 2013 07:47:58 GMT');
#
#     t.end();
# });
