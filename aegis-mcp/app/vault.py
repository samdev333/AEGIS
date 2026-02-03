"""HashiCorp Vault integration for secret retrieval."""
import os
import logging
from typing import Any

logger = logging.getLogger(__name__)


def get_vault_config() -> dict[str, str | None]:
    """Get Vault configuration from environment variables."""
    return {
        "addr": os.environ.get("VAULT_ADDR"),
        "token": os.environ.get("VAULT_TOKEN"),
        "namespace": os.environ.get("VAULT_NAMESPACE"),
        "kv_mount": os.environ.get("VAULT_KV_MOUNT", "secret"),
        "secret_path": os.environ.get("VAULT_SECRET_PATH", "aegis/mcp"),
    }


def is_vault_configured() -> bool:
    """Check if Vault is configured (minimum: VAULT_ADDR and VAULT_TOKEN)."""
    config = get_vault_config()
    return bool(config["addr"] and config["token"])


def load_vault_secret() -> dict[str, Any]:
    """
    Attempt to load the AEGIS MCP secret from Vault.

    Returns:
        dict with:
        - vault_secret_loaded: bool
        - error: str (if failed)

    Note: The actual secret value is NEVER returned to callers.
    This function only confirms whether the secret was successfully read.
    """
    if not is_vault_configured():
        return {
            "vault_secret_loaded": False,
            "error": "Vault not configured (VAULT_ADDR or VAULT_TOKEN missing)",
        }

    config = get_vault_config()

    try:
        import requests

        # Build the Vault API URL for KV v2
        # KV v2 path: {mount}/data/{path}
        vault_url = f"{config['addr']}/v1/{config['kv_mount']}/data/{config['secret_path']}"

        headers = {
            "X-Vault-Token": config["token"],
        }

        # Add namespace header if configured
        if config["namespace"]:
            headers["X-Vault-Namespace"] = config["namespace"]

        response = requests.get(vault_url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            # Verify the secret data exists (don't return it!)
            if data.get("data", {}).get("data"):
                logger.info("Successfully loaded secret from Vault")
                return {"vault_secret_loaded": True}
            else:
                return {
                    "vault_secret_loaded": False,
                    "error": "Secret exists but has no data",
                }
        elif response.status_code == 404:
            return {
                "vault_secret_loaded": False,
                "error": f"Secret not found at path: {config['kv_mount']}/{config['secret_path']}",
            }
        else:
            return {
                "vault_secret_loaded": False,
                "error": f"Vault returned status {response.status_code}",
            }

    except ImportError:
        # requests library not available - try urllib
        try:
            import urllib.request
            import urllib.error
            import json

            vault_url = f"{config['addr']}/v1/{config['kv_mount']}/data/{config['secret_path']}"

            req = urllib.request.Request(vault_url)
            req.add_header("X-Vault-Token", config["token"])
            if config["namespace"]:
                req.add_header("X-Vault-Namespace", config["namespace"])

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                if data.get("data", {}).get("data"):
                    logger.info("Successfully loaded secret from Vault (urllib)")
                    return {"vault_secret_loaded": True}
                else:
                    return {
                        "vault_secret_loaded": False,
                        "error": "Secret exists but has no data",
                    }

        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {
                    "vault_secret_loaded": False,
                    "error": f"Secret not found at path: {config['kv_mount']}/{config['secret_path']}",
                }
            return {
                "vault_secret_loaded": False,
                "error": f"Vault returned status {e.code}",
            }
        except Exception as e:
            logger.warning(f"Failed to load Vault secret (urllib): {e}")
            return {
                "vault_secret_loaded": False,
                "error": str(e),
            }

    except Exception as e:
        logger.warning(f"Failed to load Vault secret: {e}")
        return {
            "vault_secret_loaded": False,
            "error": str(e),
        }


def load_vault_token() -> dict[str, Any]:
    """
    Alias for load_vault_secret() - attempts to read the MCP token from Vault.

    This is called AFTER authorization succeeds.
    The token value is never returned; only success/failure status.
    """
    return load_vault_secret()
