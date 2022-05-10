using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SubMenuController : MonoBehaviour
{
    public GameObject m_SubMenu;
    public GameObject m_Next;


    public void Next_btn_clicked()
    {
        m_SubMenu.SetActive(false);
        m_Next.SetActive(true);
    }
    public void Next_back_clicked()
    {
        m_SubMenu.SetActive(true);
        m_Next.SetActive(false);
    }

}
