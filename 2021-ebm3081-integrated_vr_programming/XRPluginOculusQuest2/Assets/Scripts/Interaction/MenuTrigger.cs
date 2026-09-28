using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MenuTrigger : MonoBehaviour
{
    public GameObject m_MainMenu;

    private void OnTriggerEnter(Collider other)
    {
        m_MainMenu.SetActive(true);
    }

}
