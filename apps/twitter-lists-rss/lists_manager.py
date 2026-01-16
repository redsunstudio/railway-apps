"""
Lists Manager
Manages stored Twitter lists configuration
Uses JSON file storage for simplicity (can be upgraded to SQLite/Redis)
"""

import json
import os
import logging
from datetime import datetime, timezone
from threading import Lock
import uuid

logger = logging.getLogger(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'lists_data.json')


class ListsManager:
    """Manages Twitter lists configuration"""

    def __init__(self, data_file=None):
        self.data_file = data_file or DATA_FILE
        self.lock = Lock()
        self._ensure_data_file()

    def _ensure_data_file(self):
        """Ensure data file exists"""
        if not os.path.exists(self.data_file):
            self._save_data({'lists': []})

    def _load_data(self):
        """Load data from file"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {'lists': []}

    def _save_data(self, data):
        """Save data to file"""
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def get_all_lists(self):
        """Get all configured lists"""
        with self.lock:
            data = self._load_data()
            return data.get('lists', [])

    def get_list(self, list_id):
        """Get a specific list by ID"""
        with self.lock:
            data = self._load_data()
            for lst in data.get('lists', []):
                if lst['list_id'] == list_id:
                    return lst
            return None

    def add_list(self, list_id, url, name):
        """
        Add a new list

        Args:
            list_id: Twitter list ID
            url: Original Twitter list URL
            name: Human-readable name

        Returns:
            The created list dict, or None if it already exists
        """
        with self.lock:
            data = self._load_data()
            lists = data.get('lists', [])

            # Check if already exists
            for lst in lists:
                if lst['list_id'] == list_id:
                    return None

            # Create new list entry
            new_list = {
                'id': str(uuid.uuid4())[:8],
                'list_id': list_id,
                'url': url,
                'name': name,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'last_fetched': None,
                'enabled': True
            }

            lists.append(new_list)
            data['lists'] = lists
            self._save_data(data)

            logger.info(f"Added list: {name} ({list_id})")
            return new_list

    def delete_list(self, list_id):
        """
        Delete a list by ID

        Args:
            list_id: Twitter list ID

        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            data = self._load_data()
            lists = data.get('lists', [])

            original_count = len(lists)
            lists = [lst for lst in lists if lst['list_id'] != list_id]

            if len(lists) < original_count:
                data['lists'] = lists
                self._save_data(data)
                logger.info(f"Deleted list: {list_id}")
                return True

            return False

    def update_list(self, list_id, name=None, enabled=None):
        """
        Update a list's properties

        Args:
            list_id: Twitter list ID
            name: New name (optional)
            enabled: Enable/disable (optional)

        Returns:
            Updated list dict, or None if not found
        """
        with self.lock:
            data = self._load_data()
            lists = data.get('lists', [])

            for lst in lists:
                if lst['list_id'] == list_id:
                    if name is not None:
                        lst['name'] = name
                    if enabled is not None:
                        lst['enabled'] = enabled
                    lst['updated_at'] = datetime.now(timezone.utc).isoformat()

                    data['lists'] = lists
                    self._save_data(data)
                    logger.info(f"Updated list: {list_id}")
                    return lst

            return None

    def update_last_fetched(self, list_id):
        """Update the last_fetched timestamp for a list"""
        with self.lock:
            data = self._load_data()
            lists = data.get('lists', [])

            for lst in lists:
                if lst['list_id'] == list_id:
                    lst['last_fetched'] = datetime.now(timezone.utc).isoformat()
                    data['lists'] = lists
                    self._save_data(data)
                    return True

            return False

    def list_exists(self, list_id):
        """Check if a list exists"""
        return self.get_list(list_id) is not None


# Test
if __name__ == '__main__':
    manager = ListsManager()

    # Test adding a list
    result = manager.add_list(
        list_id='12345',
        url='https://twitter.com/i/lists/12345',
        name='Test List'
    )
    print(f"Added: {result}")

    # Test getting all lists
    all_lists = manager.get_all_lists()
    print(f"All lists: {all_lists}")

    # Test updating
    updated = manager.update_list('12345', name='Updated Test List')
    print(f"Updated: {updated}")

    # Test deleting
    deleted = manager.delete_list('12345')
    print(f"Deleted: {deleted}")
